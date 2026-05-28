import streamlit as st
from mock_results import get_mock_model_results
from stats import (
    calculate_compliance_metrics,
    calculate_hashtag_performance,
    calculate_engagement_metrics,
    detect_serial_hijackers,
    create_compliance_pie_chart,
    create_hashtag_risk_heatmap,
    create_engagement_comparison_chart,
    create_post_audit_table
)


def render_analytics_dashboard():
    """
    Main analytics dashboard with pink/blue/black theme
    """
    
    # Load data
    df = get_mock_model_results()
    
    # Calculate all statistics
    metrics = calculate_compliance_metrics(df)
    hashtag_perf = calculate_hashtag_performance(df)
    engagement = calculate_engagement_metrics(df)
    serial_hijackers = detect_serial_hijackers(df)
    
    # Top KPI Cards with visible question marks
    st.markdown("### Campaign Intelligence Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("**Total Posts**", help="Total number of posts collected using your campaign hashtags")
        st.metric(
            label="",
            value=f"{metrics['total_posts']:,}",
            delta=None,
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("**Brand Alignment Score**", help="Percentage of posts that genuinely match your campaign intent (primary KPI)")
        st.metric(
            label="",
            value=f"{metrics['brand_alignment_score']}%",
            delta=f"{metrics['aligned_posts']} aligned",
            delta_color="normal",
            label_visibility="collapsed"
        )
    
    with col3:
        st.markdown("**Hashtag Hijack Rate**", help="Percentage of spam or irrelevant posts hijacking your hashtags")
        st.metric(
            label="",
            value=f"{metrics['hijacking_rate']}%",
            delta=f"{metrics['misaligned_posts']} hijacked",
            delta_color="inverse",
            label_visibility="collapsed"
        )
    
    with col4:
        st.markdown("**Engagement Quality**", help="Percentage of engagement from authentic campaign-aligned content")
        st.metric(
            label="",
            value=f"{engagement['engagement_quality_score']}%",
            delta="Clean engagement",
            delta_color="normal",
            label_visibility="collapsed"
        )
    
    with col5:
        st.markdown("**Wasted Reach**", help="Estimated impressions lost to spam and hijacked posts - represents marketing waste")
        st.metric(
            label="",
            value=f"{metrics['wasted_reach']:,}",
            delta=f"{metrics['wasted_reach_percentage']}% of total",
            delta_color="inverse",
            label_visibility="collapsed"
        )
    
    st.divider()
    
    # Real-Time Threat Detection
    high_risk_hashtags = hashtag_perf[hashtag_perf['Hijack_Rate'] >= 50]
    if len(high_risk_hashtags) > 0:
        for _, row in high_risk_hashtags.iterrows():
            st.markdown(
                f'<div style="background-color: #fee2e2; border-left: 5px solid #ef4444; padding: 12px; border-radius: 6px; margin-bottom: 10px;">'
                f'<span style="color: #78350f; font-family: Inter, sans-serif; font-weight: 800; font-size: 14px;">'
                f" THREAT ALERT: Spam spike detected in {row['Hashtag']} — Hijack rate: {row['Hijack_Rate']}% ({row['Misaligned_Posts']} spam posts)"
                f'</span></div>', 
                unsafe_allow_html=True
            )
    
    medium_risk_hashtags = hashtag_perf[(hashtag_perf['Hijack_Rate'] >= 30) & (hashtag_perf['Hijack_Rate'] < 50)]
    if len(medium_risk_hashtags) > 0:
        for _, row in medium_risk_hashtags.iterrows():
            st.markdown(
                f'<div style="background-color: #fef9c3; border-left: 5px solid #eab308; padding: 12px; border-radius: 6px; margin-bottom: 10px;">'
                f'<span style="color: #78350f; font-family: Inter, sans-serif; font-weight: 800; font-size: 14px;">'
                f" MODERATE RISK: {row['Hashtag']} showing elevated hijack activity — {row['Hijack_Rate']}% ({row['Misaligned_Posts']} spam posts)"
                f'</span></div>', 
                unsafe_allow_html=True
            )
    
    st.divider()
    
    # Serial Hijacker Detection
    if len(serial_hijackers) > 0:
        st.markdown("### Serial Hijacker Detection")
        st.caption("Users repeatedly posting spam across your campaign hashtags")
        
        # Display serial hijackers
        for _, hijacker in serial_hijackers.iterrows():
            col_a, col_b, col_c, col_d = st.columns([3, 2, 2, 2])
            with col_a:
                st.markdown(f"**{hijacker['Username']}**")
            with col_b:
                st.markdown(f"{hijacker['Spam_Posts']} spam posts")
            with col_c:
                st.markdown(f"{hijacker['Total_Engagement']:,} engagement")
            with col_d:
                st.markdown(f"**{hijacker['Threat_Level']}** THREAT")
        
        st.divider()
    
    # Visual Analytics
    st.markdown("### Campaign Integrity Analytics")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        col_title, col_help = st.columns([10, 1])
        with col_title:
            st.markdown("#### Brand Alignment Distribution")
        with col_help:
            st.markdown("<span class='custom-help-icon'></span>", 
                        unsafe_allow_html=True, 
                        help="Visual breakdown of aligned posts (genuine campaign content) vs hijacked posts (spam/scams)")
        pie_chart = create_compliance_pie_chart(metrics)
        
        pie_chart.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
        )
        st.plotly_chart(pie_chart, use_container_width=True)
    
    with chart_col2:
        col_title2, col_help2 = st.columns([10, 1])
        with col_title2:
            st.markdown("#### Engagement Quality Analysis")
        with col_help2:
            st.markdown("<span class='custom-help-icon'></span>", 
                        unsafe_allow_html=True,
                        help="Compares engagement between authentic posts vs spam to detect if hijackers are stealing audience attention")
        engagement_chart = create_engagement_comparison_chart(engagement)
        
        engagement_chart.update_layout(
            xaxis=dict(title=""), 
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
        )
        st.plotly_chart(engagement_chart, use_container_width=True)
    
    # Campaign Integrity Heatmap
    col_title3, col_help3 = st.columns([20, 1])
    with col_title3:
        st.markdown("#### Campaign Integrity Heatmap")
    with col_help3:
        st.markdown("<span class='custom-help-icon'></span>", 
                   unsafe_allow_html=True,
                   help="Real-time threat visualization showing hijack severity per hashtag. Light orange = healthy, medium orange = moderate risk, dark orange = severe hijacking")
    heatmap = create_hashtag_risk_heatmap(hashtag_perf)
    st.plotly_chart(heatmap, use_container_width=True)
    
    st.divider()
    
    # Hashtag Risk Analysis Table
    st.markdown("### Hashtag Risk Analysis")
    st.caption("Detailed breakdown of each hashtag ranked by hijack severity")
    
    risk_display = hashtag_perf[['Hashtag', 'Total_Posts', 'Aligned_Posts', 'Misaligned_Posts', 
                                   'Brand_Alignment', 'Hijack_Rate', 'Risk_Level']]
    st.dataframe(risk_display, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # AI-Powered Post Audit Feed
    col_title4, col_help4 = st.columns([20, 1])
    with col_title4:
        st.markdown("### AI-Powered Post Audit Feed")
    with col_help4:
        st.markdown(
            "<span class='custom-help-icon'></span>", 
            unsafe_allow_html=True,
            help="Top posts by engagement with AI classification, confidence scores, and spam detection reasons. Shows exactly which posts are hijacking your campaign"
        )
    
    col_slider, col_space = st.columns([3, 7])
    with col_slider:
        top_n = st.slider("Number of posts to display", min_value=5, max_value=50, value=20, step=5)
    
    audit_table = create_post_audit_table(df, top_n=top_n)
    
    st.dataframe(
        audit_table,
        use_container_width=True,
        height=450,
        hide_index=True,
        column_config={
            "Engagement_Score": st.column_config.NumberColumn(
                "Total Engagement",
                help="Likes + Comments",
                format="%d"
            ),
            "AI_Confidence": st.column_config.NumberColumn(
                "AI Confidence",
                help="Model confidence score (0.0 - 1.0)",
                format="%.2f"
            ),
            "Spam_Reason": st.column_config.TextColumn(
                "AI Detection Reason",
                help="Explanation of classification",
                width="large"
            ),
            "Status": st.column_config.TextColumn(
                "Status",
                help="Aligned or Hijacked"
            )
        }
    )
    
    # Detailed Engagement Breakdown
    with st.expander("Detailed Engagement Breakdown"):
        eng_col1, eng_col2, eng_col3 = st.columns(3)
        
        with eng_col1:
            st.markdown("**Aligned Posts (Clean Engagement)**")
            st.write(f"Total Likes: {engagement['aligned_total_likes']:,}")
            st.write(f"Total Comments: {engagement['aligned_total_comments']:,}")
            st.write(f"Total Engagement: {engagement['aligned_total_engagement']:,}")
            st.write(f"Avg Likes: {engagement['aligned_avg_likes']:.1f}")
            st.write(f"Avg Comments: {engagement['aligned_avg_comments']:.1f}")
        
        with eng_col2:
            st.markdown("**Hijacked Posts (Polluted Engagement)**")
            st.write(f"Total Likes: {engagement['misaligned_total_likes']:,}")
            st.write(f"Total Comments: {engagement['misaligned_total_comments']:,}")
            st.write(f"Total Engagement: {engagement['misaligned_total_engagement']:,}")
            st.write(f"Avg Likes: {engagement['misaligned_avg_likes']:.1f}")
            st.write(f"Avg Comments: {engagement['misaligned_avg_comments']:.1f}")
        
        with eng_col3:
            st.markdown("**Quality Metrics**")
            st.write(f"Engagement Quality Score: **{engagement['engagement_quality_score']}%**")
            st.write(f"Total Campaign Engagement: {engagement['total_engagement']:,}")
            st.write(f"Clean Engagement: {engagement['aligned_total_engagement']:,}")
            st.write(f"Polluted Engagement: {engagement['misaligned_total_engagement']:,}")


if __name__ == "__main__":
    st.set_page_config(
        page_title="TagAlign AI - Campaign Protection Platform",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Auto-shutdown when browser closes
    import streamlit.components.v1 as components
    import os
    import time
    import threading
    
    if 'last_heartbeat' not in st.session_state:
        st.session_state['last_heartbeat'] = time.time()
    if 'shutdown_watcher_started' not in st.session_state:
        st.session_state['shutdown_watcher_started'] = False
    
    query_params = st.query_params
    if "heartbeat" in query_params:
        st.session_state['last_heartbeat'] = time.time()
        st.stop()
    
    def shutdown_watcher():
        while True:
            time.sleep(2)
            age = time.time() - st.session_state.get('last_heartbeat', time.time())
            if age > 8:
                os._exit(0)
    
    if not st.session_state['shutdown_watcher_started']:
        t = threading.Thread(target=shutdown_watcher, daemon=True)
        t.start()
        st.session_state['shutdown_watcher_started'] = True
    
    components.html("""
    <script>
    setInterval(function() {
        fetch(window.location.href.split('?')[0] + '?heartbeat=1', { method: 'GET' });
    }, 3000);
    </script>
    """, height=0, width=0)
    
    # Custom CSS Blocks
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #dbeafe 100%);
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.98);
        padding: 15px;
        border-radius: 10px;
        border: 2px solid rgba(251, 146, 60, 0.3);
        box-shadow: 0 4px 12px rgba(251, 146, 60, 0.1);
    }
    .stMetric label {
        color: #78350f !important;
        font-weight: 700 !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #78350f !important;
        font-weight: 800 !important;
    }
    h1, h2, h3, h4 {
        color: #78350f !important;
        font-family: 'Inter', sans-serif;
        font-weight: 800 !important;
    }
    .stMarkdown {
        color: #78350f !important;
    }
    .stAlert {
        background: rgba(255, 255, 255, 0.98);
    }

    div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p,
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] div {
        color: #78350f !important;
        font-weight: 800 !important;
        font-size: 14.5px !important;
    }
    
    div[data-testid="stAlert"] svg {
        fill: #78350f !important;
    }

    div[data-testid="stMarkdownContainer"] [property="blockquote"] + span, 
    div[data-testid="stMarkdownContainer"] svg {
        color: #78350f !important;
        fill: #78350f !important;
    }
    
    .custom-help-icon {
        font-size: 16px !important; 
        font-weight: 900 !important; 
        color: #78350f !important;
        cursor: help;
    }
    
    div[data-testid="stMetric"] div div svg {
        fill: #78350f !important;
    }

    /* כפיית צבע חום קריא על כל מקראות הגרפים */
    .js-plotly-plot .legendtext {
        fill: #78350f !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
    }
    
    .js-plotly-plot .gtitle, .js-plotly-plot .xtitle, .js-plotly-plot .ytitle {
        fill: #78350f !important;
    }

    .js-plotly-plot .infolayer .g-gtitle {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("TagAlign AI — Campaign Integrity & Brand Protection Platform")
    st.markdown("*Real-time hashtag hijacking detection and campaign intelligence*")
    st.markdown("---")
    
    render_analytics_dashboard()