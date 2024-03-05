import streamlit as st
import pandas as pd
import re

def process_entry(entry):
    parts = entry.split('(')
    if len(parts) > 1:
        name = parts[0].strip()
        rest = parts[1].split(')')
        if len(rest) > 1:
            pro = rest[0].strip()
            percent_part = rest[1].strip()
            percentage_match = re.search(r'\d+', percent_part)
            ipi_match = re.search(r'\[(.*?)\]', percent_part)
            percentage = int(percentage_match.group()) if percentage_match else 0
            ipi = ipi_match.group(1) if ipi_match else ""
            return name, pro, percentage, ipi
    return None, None, 0, ""

def process_file(uploaded_file):
    df = pd.read_excel(uploaded_file, engine='openpyxl', header=None)

    composers = {}
    publishers = {}
    num_tracks = 0

    if 18 in df.columns and 22 in df.columns and 26 in df.columns:
        df_full_tracks = df[df[18].astype(str).str.contains('Full', na=False)]
        num_tracks = len(df_full_tracks)

        for _, row in df_full_tracks.iterrows():
            # Process composers
            composer_entries = str(row[22]).split(',')
            for entry in composer_entries:
                name, pro, percentage, ipi = process_entry(entry)
                if name:
                    composers[name] = composers.get(name, {'pro': pro, 'ipi': ipi, 'points': 0})
                    composers[name]['points'] += percentage

            # Process publishers
            publisher_entries = str(row[26]).split(',')
            for entry in publisher_entries:
                name, pro, percentage, ipi = process_entry(entry)
                if name:
                    publishers[name] = publishers.get(name, {'pro': pro, 'ipi': ipi, 'points': 0})
                    publishers[name]['points'] += percentage

        total_points_possible = num_tracks * 100
        for composer in composers:
            composers[composer]['percentage'] = (composers[composer]['points'] / total_points_possible) * 100

        for publisher in publishers:
            publishers[publisher]['percentage'] = (publishers[publisher]['points'] / total_points_possible) * 100

        return composers, publishers, num_tracks, total_points_possible
    else:
        return None, None, 0, 0

def format_percentage(percentage):
    return f"{percentage:.2f}".rstrip('0').rstrip('.') + '%' if percentage != 0 else "0%"

st.title('Composer Contribution Analyzer')

uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx'])
if uploaded_file is not None:
    composers, publishers, num_tracks, total_points_possible = process_file(uploaded_file)
    if composers and publishers:
        # Display Composers
        sorted_composers = sorted(composers.items(), key=lambda x: x[1]['points'], reverse=True)
        formatted_composers = ", ".join([f"{name} ({info['pro']}) {format_percentage(info['percentage'])} [{info['ipi']}]" for name, info in sorted_composers])
        st.write(f"Composers: {formatted_composers}")

        # Display Publishers
        sorted_publishers = sorted(publishers.items(), key=lambda x: x[1]['percentage'], reverse=True)
        formatted_publishers = ", ".join(
            [f"{name} ({info['pro']}) {format_percentage(info['percentage'])} [{info['ipi']}]" for name, info in
             sorted_publishers])
        st.write(f"Publishers: {formatted_publishers}")

        # Album Info
        st.write(f"The album has {num_tracks} tracks ({total_points_possible} points)")

        # Composer Points

        for composer, info in sorted_composers:
            st.write(f"{composer}: {info['points']} points")


    else:
        st.write("Invalid file or file format")
