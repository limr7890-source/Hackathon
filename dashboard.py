import streamlit as st
from mock_results import get_mock_model_results
from stats import (
    calculate_compliance_metrics,
    calculate_hashtag_performance,
    calculate_engagement_metrics,
    create_compliance_pie_chart,
    create_hashtag_risk_heatmap,
    create_engagement_comparison_chart,
    create_post_audit_table
)


def render_analytics_dashboard():
    """
    הפונקציה המרכזית שמציגה את כל הדשבורד:
    1. KPI Cards למעלה (מדדים עיקריים - Brand Alignment Score™)
    2. גרפים אינטראקטיביים באמצע (Campaign Integrity Heatmap™)
    3. טבלת Post Audit למטה (AI Explanation Layer)
    """
    
    # ─── שלב 1: טוען את הנתונים (כרגע מדומים, אחר כך אמיתיים) ───
    df = get_mock_model_results()
    
    # ─── שלב 2: מחשב את כל הסטטיסטיקות ───
    metrics = calculate_compliance_metrics(df)
    hashtag_perf = calculate_hashtag_performance(df)
    engagement = calculate_engagement_metrics(df)
    
    # ─── שלב 3: מציג KPI Cards גדולים למעלה (Enterprise Metrics) ───
    st.markdown("### 🎯 Campaign Intelligence Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Posts",
            value=f"{metrics['total_posts']:,}",
            delta=None,
            help="Total number of posts collected using your campaign hashtags"
        )
    
    with col2:
        st.metric(
            label="🟢 Brand Alignment Score™",
            value=f"{metrics['brand_alignment_score']}%",
            delta=f"{metrics['aligned_posts']} aligned",
            delta_color="normal",
            help="Percentage of posts that genuinely match your campaign intent and serve your brand (primary KPI)"
        )
    
    with col3:
        st.metric(
            label="🔴 Hashtag Hijack Rate",
            value=f"{metrics['hijacking_rate']}%",
            delta=f"{metrics['misaligned_posts']} hijacked",
            delta_color="inverse",
            help="Percentage of spam or irrelevant posts that hijacked your hashtags for their own promotion"
        )
    
    with col4:
        st.metric(
            label="💎 Engagement Quality",
            value=f"{engagement['engagement_quality_score']}%",
            delta="Clean engagement",
            delta_color="normal",
            help="Percentage of total engagement (likes + comments) that comes from authentic, campaign-aligned content"
        )
    
    with col5:
        st.metric(
            label="⚠️ Wasted Reach",
            value=f"{metrics['wasted_reach']:,}",
            delta=f"{metrics['wasted_reach_percentage']}% of total",
            delta_color="inverse",
            help="Estimated impressions lost to spam and hijacked posts - represents marketing waste"
        )
    
    st.divider()
    
    # ─── שלב 4: Real-Time Threat Detection ───
    # בודק אם יש האשטאג עם Hijack Rate מעל 50%
    high_risk_hashtags = hashtag_perf[hashtag_perf['Hijack_Rate'] >= 50]
    if len(high_risk_hashtags) > 0:
        for _, row in high_risk_hashtags.iterrows():
            st.error(f"🚨 **THREAT ALERT**: Spam spike detected in **{row['Hashtag']}** — Hijack rate: **{row['Hijack_Rate']}%** ({row['Misaligned_Posts']} spam posts)")
    
    medium_risk_hashtags = hashtag_perf[(hashtag_perf['Hijack_Rate'] >= 30) & (hashtag_perf['Hijack_Rate'] < 50)]
    if len(medium_risk_hashtags) > 0:
        for _, row in medium_risk_hashtags.iterrows():
            st.warning(f"⚠️ **MODERATE RISK**: {row['Hashtag']} showing elevated hijack activity — {row['Hijack_Rate']}% ({row['Misaligned_Posts']} spam posts)")
    
    st.divider()
    
    # ─── שלב 5: מציג גרפים אינטראקטיביים ───
    st.markdown("### 📊 Campaign Integrity Analytics")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # גרף עוגה - חלוקת Brand Alignment
        col_title, col_help = st.columns([10, 1])
        with col_title:
            st.markdown("#### Brand Alignment Distribution")
        with col_help:
            st.markdown("❓", help="Visual breakdown of aligned posts (genuine campaign content) vs hijacked posts (spam/scams)")
        pie_chart = create_compliance_pie_chart(metrics)
        st.plotly_chart(pie_chart, use_container_width=True)
    
    with chart_col2:
        # גרף השוואת Engagement Quality
        col_title2, col_help2 = st.columns([10, 1])
        with col_title2:
            st.markdown("#### Engagement Quality Analysis")
        with col_help2:
            st.markdown("❓", help="Compares average engagement between authentic posts vs spam to detect if hijackers are stealing audience attention")
        engagement_chart = create_engagement_comparison_chart(engagement)
        st.plotly_chart(engagement_chart, use_container_width=True)
    
    # Campaign Integrity Heatmap™ (רוחב מלא)
    col_title3, col_help3 = st.columns([20, 1])
    with col_title3:
        st.markdown("#### 🔥 Campaign Integrity Heatmap™")
    with col_help3:
        st.markdown("❓", help="Real-time threat visualization showing hijack severity per hashtag. Green = healthy, Yellow = moderate risk, Red = severe hijacking")
    heatmap = create_hashtag_risk_heatmap(hashtag_perf)
    st.plotly_chart(heatmap, use_container_width=True)
    
    st.divider()
    
    # ─── שלב 6: Hashtag Risk Analysis Table ───
    st.markdown("### 🏷️ Hashtag Risk Analysis")
    st.caption("Detailed breakdown of each hashtag ranked by hijack severity")
    
    # מציג טבלה מסודרת לפי Risk Level
    risk_display = hashtag_perf[['Hashtag', 'Total_Posts', 'Aligned_Posts', 'Misaligned_Posts', 
                                   'Brand_Alignment', 'Hijack_Rate', 'Risk_Level']]
    st.dataframe(risk_display, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # ─── שלב 7: טבלת Post Audit עם AI Explanation Layer ───
    col_title4, col_help4 = st.columns([20, 1])
    with col_title4:
        st.markdown("### 🔍 AI-Powered Post Audit Feed")
    with col_help4:
        st.markdown("❓", help="Top posts by engagement with AI classification, confidence scores, and spam detection reasons. Shows exactly which posts are hijacking your campaign")
    
    # מאפשר למשתמש לבחור כמה פוסטים להציג
    col_slider, col_space = st.columns([3, 7])
    with col_slider:
        top_n = st.slider("Number of posts to display", min_value=5, max_value=50, value=20, step=5)
    
    audit_table = create_post_audit_table(df, top_n=top_n)
    
    # מציג את הטבלה עם עיצוב נקי
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
                help="Explanation of why the post was classified as aligned or spam",
                width="large"
            )
        }
    )
    
    # ─── שלב 8: סיכום סטטיסטי נוסף (אופציונלי) ───
    with st.expander("💡 Detailed Engagement Breakdown"):
        eng_col1, eng_col2, eng_col3 = st.columns(3)
        
        with eng_col1:
            st.markdown("**✅ Aligned Posts (Clean Engagement):**")
            st.write(f"- Total Likes: {engagement['aligned_total_likes']:,}")
            st.write(f"- Total Comments: {engagement['aligned_total_comments']:,}")
            st.write(f"- Total Engagement: {engagement['aligned_total_engagement']:,}")
            st.write(f"- Avg Likes: {engagement['aligned_avg_likes']:.1f}")
            st.write(f"- Avg Comments: {engagement['aligned_avg_comments']:.1f}")
        
        with eng_col2:
            st.markdown("**❌ Hijacked Posts (Polluted Engagement):**")
            st.write(f"- Total Likes: {engagement['misaligned_total_likes']:,}")
            st.write(f"- Total Comments: {engagement['misaligned_total_comments']:,}")
            st.write(f"- Total Engagement: {engagement['misaligned_total_engagement']:,}")
            st.write(f"- Avg Likes: {engagement['misaligned_avg_likes']:.1f}")
            st.write(f"- Avg Comments: {engagement['misaligned_avg_comments']:.1f}")
        
        with eng_col3:
            st.markdown("**📊 Quality Metrics:**")
            st.write(f"- Engagement Quality Score: **{engagement['engagement_quality_score']}%**")
            st.write(f"- Total Campaign Engagement: {engagement['total_engagement']:,}")
            st.write(f"- Clean Engagement: {engagement['aligned_total_engagement']:,}")
            st.write(f"- Polluted Engagement: {engagement['misaligned_total_engagement']:,}")


# אם מריצים את הקובץ הזה ישירות, הוא יפעיל את הדשבורד
if __name__ == "__main__":
    st.set_page_config(
        page_title="TagAlign AI - Campaign Protection Platform",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    st.title("🔮 TagAlign AI — Campaign Integrity & Brand Protection Platform")
    st.markdown("*Real-time hashtag hijacking detection and campaign intelligence*")
    st.markdown("---")
    
    render_analytics_dashboard()
