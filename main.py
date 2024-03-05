import streamlit as st
import pandas as pd
import re

def process_file(uploaded_file):
    df = pd.read_excel(uploaded_file, engine='openpyxl', header=None)

    if 18 in df.columns and 22 in df.columns:
        df_full_tracks = df[df[18].astype(str).str.contains('Full', na=False)]
        composers = {}
        pro_requirements = {}
        num_tracks = len(df_full_tracks)

        for _, row in df_full_tracks.iterrows():
            composer_data = str(row[22]).split(',')
            for composer_entry in composer_data:
                parts = composer_entry.split('(')
                if len(parts) > 1:
                    name = parts[0].strip()
                    pro_and_percent = parts[1].split(')')
                    if len(pro_and_percent) > 1:
                        pro = pro_and_percent[0].strip()
                        ipi_match = re.search(r'\[(.*?)\]', composer_entry)
                        ipi = ipi_match.group(1) if ipi_match else ""
                        percentage_match = re.search(r'\d+', pro_and_percent[1])
                        if percentage_match:
                            percentage = int(percentage_match.group())
                            points = percentage
                            composers[name] = {
                                'points': composers.get(name, {}).get('points', 0) + points,
                                'pro': pro,
                                'ipi': ipi
                            }
                            pro_requirements[pro] = pro_requirements.get(pro, 0) + points

        total_points = sum(composer['points'] for composer in composers.values())
        max_possible_points = num_tracks * 100
        for composer in composers:
            composers[composer]['percentage'] = 100 * composers[composer]['points'] / max_possible_points if max_possible_points > 0 else 0
        for pro in pro_requirements:
            pro_requirements[pro] = 100 * pro_requirements[pro] / max_possible_points if max_possible_points > 0 else 0

        return composers, pro_requirements, num_tracks, max_possible_points
    else:
        return None, None, 0, 0

def format_percentage(percentage):
    return f"{percentage:.2f}".rstrip('0').rstrip('.') + '%' if percentage != 0 else "0%"

st.title('Composer Contribution Analyzer')

uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx'])
if uploaded_file is not None:
    composers, pro_requirements, num_tracks, max_possible_points = process_file(uploaded_file)
    if composers:
        # Display Composers
        sorted_composers = sorted(composers.items(), key=lambda x: x[1]['percentage'], reverse=True)
        formatted_composers = ", ".join(
            [f"{name} ({data['pro']}) {format_percentage(data['percentage'])} [{data['ipi']}]" for name, data in sorted_composers])
        st.write(f"Composers: {formatted_composers}")

        # Displaying PRO Requirements
        formatted_pro_requirements = ", ".join([f"{pro}: {format_percentage(percentage)}" for pro, percentage in pro_requirements.items()])
        st.write(f"PRO Requirements: {formatted_pro_requirements}")

        # Album Info
        st.write(f"The album has {num_tracks} tracks ({max_possible_points} points)")

        # Composer Points
        for composer, data in sorted_composers:
            st.write(f"{composer}: {data['points']} points ({format_percentage(data['percentage'])})")

    else:
        st.write("Invalid file or file format")
