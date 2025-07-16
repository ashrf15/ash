import plotly.express as px
import streamlit as st
import pandas as pd

def recommendation(df):
    st.markdown("## 📊 Data Analysis Recommendation")
    st.subheader("🗕️ Select Date Range")

    if 'created_time' in df.columns and not df['created_time'].isna().all():
        df['created_date'] = df['created_time'].dt.date
        min_date = df['created_date'].min()
        max_date = df['created_date'].max()

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date, key="start_date_picker")
        with col2:
            end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date, key="end_date_picker")

        st.markdown(f"🗓️ **Selected Range:** `{start_date.strftime('%d/%m/%Y')}` → `{end_date.strftime('%d/%m/%Y')}`")

        reset_filter = st.button("🔁 Reset to Default", key="reset_button_2")

        if reset_filter:
            df_filtered = df.copy()
            st.info("Showing all available data (no date filter applied).")
        elif start_date > end_date:
            st.warning("⚠️ Start date is after end date. Please select a valid range.")
            return
        else:
            df_filtered = df[(df['created_date'] >= start_date) & (df['created_date'] <= end_date)]
    else:
        df_filtered = df.copy()

    st.subheader("📌 Overview Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tickets", len(df_filtered))
    col2.metric("Avg Resolution Time (hrs)", f"{df_filtered['resolution_time'].mean():.2f}")
    col3.metric("Departments Involved", df_filtered['department'].nunique())

    st.subheader("📊 Visual Insights")

    # Technician Insight
    if 'technician' in df_filtered.columns:
        tech_counts = df_filtered['technician'].value_counts().head(10).reset_index()
        tech_counts.columns = ['Technician', 'count']
        fig = px.bar(tech_counts, x='Technician', y='count', title="Top 10 Technicians")
        st.plotly_chart(fig, use_container_width=True)
        top_tech = tech_counts.iloc[0]
        if top_tech['count'] > tech_counts['count'].mean() + tech_counts['count'].std():
            st.markdown(f"**Top Technician**: {top_tech['Technician']} handled {top_tech['count']} tickets — significantly more than average.")
            st.markdown(f"**Recommendation**: Distribute tasks better or recognize {top_tech['Technician']}'s performance formally.")
        else:
            st.markdown(f"**Top Technician**: {top_tech['Technician']} is active.")
            st.markdown(f"**Recommendation**: Encourage knowledge-sharing from {top_tech['Technician']}.")

    # Department Insight
    if 'department' in df_filtered.columns:
        dept_counts = df_filtered['department'].value_counts().head(10).reset_index()
        dept_counts.columns = ['Department', 'count']
        fig = px.bar(dept_counts, x='Department', y='count', title="Top 10 Departments")
        st.plotly_chart(fig, use_container_width=True)
        slow_dept = df_filtered.groupby('department')['resolution_time'].mean().reset_index().sort_values('resolution_time', ascending=False).iloc[0]
        st.markdown(f"**Slowest Resolution Dept**: {slow_dept['department']} ({slow_dept['resolution_time']:.2f} hrs avg)")
        st.markdown("**Recommendation**: Review processes and resource allocation.")

    # SLA (Optional)
    if 'sla_hours' in df_filtered.columns:
        df_filtered['sla_met'] = df_filtered['resolution_time'] <= df_filtered['sla_hours']
        sla_rate = df_filtered['sla_met'].mean() * 100
        st.markdown(f"**SLA Compliance**: {sla_rate:.2f}%")
        if sla_rate < 80:
            st.markdown("**Recommendation**: Improve SLA adherence with alerts and better triaging.")
        else:
            st.markdown("**Recommendation**: Keep consistent or optimize further with auto-routing.")

    # Resolution Time Distribution
    if 'resolution_time' in df_filtered.columns:
        fig = px.histogram(df_filtered, x='resolution_time', nbins=30, marginal="box", title="Distribution of Resolution Time")
        st.plotly_chart(fig, use_container_width=True)
        avg_res = df_filtered['resolution_time'].mean()
        st.markdown(f"**Average**: {avg_res:.2f} hrs")
        if avg_res > 48:
            loss = (avg_res - 48) * len(df_filtered) * 50
            st.markdown(f"**Recommendation**: Optimize resolution time. Potential cost savings: ~RM {loss:,.0f}")

    # Monthly Volume
    if 'created_time' in df_filtered.columns:
        df_filtered['created_month'] = df_filtered['created_time'].dt.to_period("M").astype(str)
        monthly = df_filtered.groupby('created_month').size().reset_index(name='count')
        fig = px.line(monthly, x='created_month', y='count', title="Monthly Ticket Volume")
        st.plotly_chart(fig, use_container_width=True)
        if len(monthly) >= 6:
            mean_vol = monthly['count'].mean()
            std_vol = monthly['count'].std()
            surge = monthly[monthly['count'] > mean_vol + std_vol]['created_month'].tolist()
            if surge:
                st.markdown(f"**Surge Months**: {', '.join(surge)}")
                st.markdown("**Recommendation**: Increase staffing or preventive support in these months.")

    # Priority Distribution
    if 'priority' in df_filtered.columns:
        pri_counts = df_filtered['priority'].value_counts().reset_index()
        pri_counts.columns = ['Priority', 'Count']
        fig = px.bar(pri_counts, x='Priority', y='Count', title="Tickets by Priority")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"Most common: **{pri_counts.iloc[0]['Priority']}**")
        st.markdown(f"**Recommendation**: Ensure consistent priority assignment policies.")

    # Created Hour
    if 'created_time' in df_filtered.columns:
        df_filtered['created_hour'] = df_filtered['created_time'].dt.hour
        hour_counts = df_filtered['created_hour'].value_counts().sort_index().reset_index()
        hour_counts.columns = ['Hour', 'Count']
        fig = px.bar(hour_counts, x='Hour', y='Count', title="Tickets by Hour of Day")
        st.plotly_chart(fig, use_container_width=True)
        peak = hour_counts.iloc[hour_counts['Count'].idxmax()]['Hour']
        st.markdown(f"**Peak hour**: {peak}:00")
        st.markdown(f"**Recommendation**: Boost support coverage during this hour.")

    return df_filtered
