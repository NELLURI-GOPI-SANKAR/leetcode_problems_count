import streamlit as st
import requests
import pandas as pd
import io

def get_leetcode_submissions(username):
    url = 'https://leetcode.com/graphql'
    headers = {
        'Content-Type': 'application/json',
        'Referer': f'https://leetcode.com/{username}/',
        'User-Agent': 'Mozilla/5.0'
    }
    query = """
    query getUserProfile($username: String!) {
        matchedUser(username: $username) {
            submitStats {
                acSubmissionNum {
                    difficulty
                    count
                }
                totalSubmissionNum {
                    difficulty
                    count
                }
            }
        }
    }
    """
    variables = {'username': username}
    payload = {'query': query, 'variables': variables}
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code != 200:
        return {"Total": 0, "Easy": 0, "Medium": 0, "Hard": 0}

    data = response.json()
    if 'errors' in data or not data.get('data', {}).get('matchedUser', {}):
        return {"Total": 0, "Easy": 0, "Medium": 0, "Hard": 0}

    submission_stats = data['data']['matchedUser']['submitStats']
    ac_submissions = {entry['difficulty']: entry['count'] for entry in submission_stats['acSubmissionNum']}

    return {
        "Total": ac_submissions.get("All", 0),
        "Easy": ac_submissions.get("Easy", 0),
        "Medium": ac_submissions.get("Medium", 0),
        "Hard": ac_submissions.get("Hard", 0)
    }

st.title("LeetCode Submissions Tracker")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    results = []

    for _, row in df.iterrows():
        roll_number = row["roll_number"]
        profile_link = row["leetcode_profile"]

        if not isinstance(profile_link, str) or "leetcode.com" not in profile_link:
            continue

        username = profile_link.rstrip('/').split('/')[-1]

        # Get submission data
        submission_data = get_leetcode_submissions(username)

        # Store results
        results.append({
            "Roll Number": roll_number,
            "LeetCode Profile": profile_link,
            "Total Submissions": submission_data["Total"],
            "Easy": submission_data["Easy"],
            "Medium": submission_data["Medium"],
            "Hard": submission_data["Hard"]
        })

    if results:
        output_df = pd.DataFrame(results)
        st.write("Processed Data:")
        st.dataframe(output_df)

        # Convert DataFrame to CSV
        csv_buffer = io.StringIO()
        output_df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()

        # Provide download button
        st.download_button("Download CSV", data=csv_data, file_name="leetcode_results.csv", mime="text/csv")

    else:
        st.warning("No valid LeetCode profiles found.")
