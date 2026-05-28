import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def calculate_compliance_metrics(df):
    """
    מחשב את כל המדדים הסטטיסטיים של הקמפיין:
    - Brand Alignment Score™ (אחוז התאמה כללי)
    - Hashtag Hijack Rate (אחוז חטיפת האשטאגים)
    - מספר פוסטים מתאימים ולא מתאימים
    - Estimated Wasted Reach (טווח הגעה שאבד לספאם)
    """
    total_posts = len(df)
    aligned_posts = df[df['Model_Label'] == 1].shape[0]
    misaligned_posts = df[df['Model_Label'] == 0].shape[0]
    
    brand_alignment_score = (aligned_posts / total_posts * 100) if total_posts > 0 else 0
    hijacking_rate = (misaligned_posts / total_posts * 100) if total_posts > 0 else 0
    
    # חישוב Estimated Wasted Reach
    if 'Estimated_Reach' in df.columns:
        total_reach = df['Estimated_Reach'].sum()
        wasted_reach = df[df['Model_Label'] == 0]['Estimated_Reach'].sum()
        wasted_reach_percentage = (wasted_reach / total_reach * 100) if total_reach > 0 else 0
    else:
        # fallback אם אין עמודת Reach - משתמש בלייקים כהערכה
        total_reach = df['Likes'].sum()
        wasted_reach = df[df['Model_Label'] == 0]['Likes'].sum()
        wasted_reach_percentage = (wasted_reach / total_reach * 100) if total_reach > 0 else 0
    
    return {
        "total_posts": total_posts,
        "aligned_posts": aligned_posts,
        "misaligned_posts": misaligned_posts,
        "brand_alignment_score": round(brand_alignment_score, 1),
        "hijacking_rate": round(hijacking_rate, 1),
        "wasted_reach": int(wasted_reach),
        "wasted_reach_percentage": round(wasted_reach_percentage, 1),
        "total_reach": int(total_reach)
    }


def calculate_hashtag_performance(df):
    """
    מחשב ביצועים לפי האשטאג (Hashtag Risk Analysis):
    - כמה פוסטים יש לכל האשטאג
    - כמה מהם מתאימים (1) וכמה לא (0)
    - אחוז התאמה לכל האשטאג
    - Risk Level (High/Medium/Low) לפי Hijack Rate
    """
    hashtag_stats = df.groupby('Target_Hashtag').agg({
        'Model_Label': ['count', 'sum']
    }).reset_index()
    
    hashtag_stats.columns = ['Hashtag', 'Total_Posts', 'Aligned_Posts']
    hashtag_stats['Misaligned_Posts'] = hashtag_stats['Total_Posts'] - hashtag_stats['Aligned_Posts']
    hashtag_stats['Hijack_Rate'] = ((hashtag_stats['Misaligned_Posts'] / hashtag_stats['Total_Posts']) * 100).round(1)
    hashtag_stats['Brand_Alignment'] = ((hashtag_stats['Aligned_Posts'] / hashtag_stats['Total_Posts']) * 100).round(1)
    
    # חישוב Risk Level
    def calculate_risk(hijack_rate):
        if hijack_rate >= 50:
            return "🔴 High Risk"
        elif hijack_rate >= 30:
            return "🟡 Medium Risk"
        else:
            return "🟢 Low Risk"
    
    hashtag_stats['Risk_Level'] = hashtag_stats['Hijack_Rate'].apply(calculate_risk)
    
    # מסדר לפי Hijack Rate (הכי מסוכן קודם)
    hashtag_stats = hashtag_stats.sort_values('Hijack_Rate', ascending=False)
    
    return hashtag_stats


def calculate_engagement_metrics(df):
    """
    מחשב מדדי מעורבות (Engagement Quality Score):
    - סך כל הלייקים והתגובות לפוסטים מתאימים (Clean Engagement)
    - סך כל הלייקים והתגובות לפוסטים לא מתאימים (Polluted Engagement)
    - ממוצע מעורבות לפי סוג פוסט
    - Engagement Quality Score (אחוז המעורבות האיכותית)
    """
    aligned_df = df[df['Model_Label'] == 1]
    misaligned_df = df[df['Model_Label'] == 0]
    
    aligned_total_engagement = aligned_df['Likes'].sum() + aligned_df['Comments'].sum()
    misaligned_total_engagement = misaligned_df['Likes'].sum() + misaligned_df['Comments'].sum()
    total_engagement = aligned_total_engagement + misaligned_total_engagement
    
    engagement_quality_score = (aligned_total_engagement / total_engagement * 100) if total_engagement > 0 else 0
    
    engagement_stats = {
        "aligned_total_likes": aligned_df['Likes'].sum(),
        "aligned_total_comments": aligned_df['Comments'].sum(),
        "aligned_total_engagement": aligned_total_engagement,
        "aligned_avg_likes": round(aligned_df['Likes'].mean(), 1) if len(aligned_df) > 0 else 0,
        "aligned_avg_comments": round(aligned_df['Comments'].mean(), 1) if len(aligned_df) > 0 else 0,
        
        "misaligned_total_likes": misaligned_df['Likes'].sum(),
        "misaligned_total_comments": misaligned_df['Comments'].sum(),
        "misaligned_total_engagement": misaligned_total_engagement,
        "misaligned_avg_likes": round(misaligned_df['Likes'].mean(), 1) if len(misaligned_df) > 0 else 0,
        "misaligned_avg_comments": round(misaligned_df['Comments'].mean(), 1) if len(misaligned_df) > 0 else 0,
        
        "engagement_quality_score": round(engagement_quality_score, 1),
        "total_engagement": total_engagement
    }
    
    return engagement_stats


def create_compliance_pie_chart(metrics):
    """
    יוצר גרף עוגה (Pie Chart) שמראה את החלוקה בין פוסטים מתאימים ולא מתאימים
    (Brand Alignment Score™ Visualization)
    """
    labels = ['✅ Aligned Posts', '❌ Hijacked Posts']
    values = [metrics['aligned_posts'], metrics['misaligned_posts']]
    colors = ['#10b981', '#ef4444']  # ירוק ואדום למראה מקצועי יותר
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        hole=0.4,
        textinfo='label+percent',
        textfont=dict(size=14, color='white', family='Inter', weight=600)
    )])
    
    fig.update_layout(
        title="Brand Alignment Distribution",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', family='Inter'),
        showlegend=True,
        height=400
    )
    
    return fig


def create_hashtag_risk_heatmap(hashtag_stats):
    """
    יוצר Campaign Integrity Heatmap™ - מפת חום שמראה את רמת הסיכון של כל האשטאג
    """
    # מכין צבעים לפי Hijack Rate
    colors = []
    for rate in hashtag_stats['Hijack_Rate']:
        if rate >= 50:
            colors.append('#ef4444')  # אדום - High Risk
        elif rate >= 30:
            colors.append('#f59e0b')  # כתום - Medium Risk
        else:
            colors.append('#10b981')  # ירוק - Low Risk
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=hashtag_stats['Hashtag'],
        y=hashtag_stats['Hijack_Rate'],
        name='Hijack Rate',
        marker_color=colors,
        text=[f"{rate}%" for rate in hashtag_stats['Hijack_Rate']],
        textposition='auto',
        textfont=dict(size=14, color='white', family='Inter', weight=700),
        hovertemplate='<b>%{x}</b><br>Hijack Rate: %{y}%<br><extra></extra>'
    ))
    
    fig.update_layout(
        title="Campaign Integrity Heatmap™",
        xaxis_title="Hashtag",
        yaxis_title="Hijack Rate (%)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(30,41,59,0.3)',
        font=dict(color='white', family='Inter'),
        showlegend=False,
        height=450,
        yaxis=dict(range=[0, 100])
    )
    
    # הוספת קווי התראה
    fig.add_hline(y=50, line_dash="dash", line_color="red", opacity=0.5, 
                  annotation_text="High Risk Threshold", annotation_position="right")
    fig.add_hline(y=30, line_dash="dash", line_color="orange", opacity=0.5,
                  annotation_text="Medium Risk Threshold", annotation_position="right")
    
    return fig


def create_engagement_comparison_chart(engagement_stats):
    """
    יוצר גרף השוואה של מעורבות בין פוסטים מתאימים ולא מתאימים
    """
    categories = ['Avg Likes', 'Avg Comments']
    aligned_values = [engagement_stats['aligned_avg_likes'], engagement_stats['aligned_avg_comments']]
    misaligned_values = [engagement_stats['misaligned_avg_likes'], engagement_stats['misaligned_avg_comments']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=categories,
        y=aligned_values,
        name='Aligned Posts',
        marker_color='#38bdf8',
        text=[f"{v:.1f}" for v in aligned_values],
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        x=categories,
        y=misaligned_values,
        name='Misaligned Posts',
        marker_color='#f472b6',
        text=[f"{v:.1f}" for v in misaligned_values],
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Engagement Comparison: Aligned vs Misaligned",
        xaxis_title="Metric",
        yaxis_title="Average Count",
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(30,41,59,0.3)',
        font=dict(color='white', family='Inter'),
        showlegend=True,
        height=400
    )
    
    return fig


def create_post_audit_table(df, top_n=20):
    """
    יוצר טבלה מסודרת של הפוסטים המובילים עם הסיווג שלהם
    מוסיף עמודה ויזואלית של Status (✅ Aligned / ❌ Misaligned)
    כולל AI Confidence Score ו-Spam Reason (AI Explanation Layer)
    מציג רק את top_n הפוסטים עם המעורבות הגבוהה ביותר
    """
    audit_df = df.copy()
    audit_df['Status'] = audit_df['Model_Label'].apply(lambda x: '✅ Aligned' if x == 1 else '❌ Hijacked')
    audit_df['Engagement_Score'] = audit_df['Likes'] + audit_df['Comments']
    
    # מסדר לפי Engagement Score (הכי פופולרי קודם)
    audit_df = audit_df.sort_values('Engagement_Score', ascending=False)
    
    # לוקח רק את top_n הפוסטים המובילים
    audit_df = audit_df.head(top_n)
    
    # בוחר את העמודות הרלוונטיות לתצוגה (כולל AI fields אם קיימים)
    columns_to_show = ['Target_Hashtag', 'Post_Text', 'Likes', 'Comments', 'Status', 'Engagement_Score']
    
    if 'AI_Confidence' in audit_df.columns:
        columns_to_show.append('AI_Confidence')
    if 'Spam_Reason' in audit_df.columns:
        columns_to_show.append('Spam_Reason')
    
    display_df = audit_df[columns_to_show]
    
    return display_df


# אם מריצים את הקובץ הזה ישירות, הוא יריץ דוגמה עם נתונים מדומים
if __name__ == "__main__":
    from mock_results import get_mock_model_results
    
    print("=== Testing Stats Module ===\n")
    
    # טוען נתונים מדומים
    df = get_mock_model_results()
    
    # מחשב מדדים
    metrics = calculate_compliance_metrics(df)
    print("📊 Compliance Metrics:")
    print(f"   Total Posts: {metrics['total_posts']}")
    print(f"   Aligned: {metrics['aligned_posts']} ({metrics['compliance_rate']}%)")
    print(f"   Misaligned: {metrics['misaligned_posts']} ({metrics['hijacking_rate']}%)\n")
    
    # ביצועים לפי האשטאג
    hashtag_perf = calculate_hashtag_performance(df)
    print("🏷️ Hashtag Performance:")
    print(hashtag_perf.to_string(index=False))
    print()
    
    # מדדי מעורבות
    engagement = calculate_engagement_metrics(df)
    print("💬 Engagement Metrics:")
    print(f"   Aligned Avg Likes: {engagement['aligned_avg_likes']}")
    print(f"   Misaligned Avg Likes: {engagement['misaligned_avg_likes']}")
    print()
    
    print("✅ All stats calculations working perfectly!")
