import pandas as pd
import plotly.graph_objects as go


# Color scheme: Orange shades for charts, light blue background
COLORS = {
    'orange': '#fb923c',           # Main orange for hijacked
    'light_orange': '#fdba74',     # Light orange for aligned
    'dark_text': '#422006',        # Dark brown text (bold and readable)
    'light_bg': 'rgba(255, 255, 255, 1)',      # Pure white background
    'chart_bg': 'rgba(254, 252, 232, 0.9)',    # Very light cream for charts
    'white': '#ffffff'
}


def calculate_compliance_metrics(df):
    """
    Calculate all campaign metrics including Brand Alignment Score and Wasted Reach
    """
    total_posts = len(df)
    aligned_posts = df[df['Model_Label'] == 1].shape[0]
    misaligned_posts = df[df['Model_Label'] == 0].shape[0]
    
    brand_alignment_score = (aligned_posts / total_posts * 100) if total_posts > 0 else 0
    hijacking_rate = (misaligned_posts / total_posts * 100) if total_posts > 0 else 0
    
    # Calculate Estimated Wasted Reach
    if 'Estimated_Reach' in df.columns:
        total_reach = df['Estimated_Reach'].sum()
        wasted_reach = df[df['Model_Label'] == 0]['Estimated_Reach'].sum()
        wasted_reach_percentage = (wasted_reach / total_reach * 100) if total_reach > 0 else 0
    else:
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


def detect_serial_hijackers(df, min_spam_posts=2):
    """
    Detect users who repeatedly post spam (Serial Hijackers)
    Returns DataFrame of serial hijackers ranked by spam count
    """
    if 'Username' not in df.columns:
        return pd.DataFrame()
    
    # Count spam posts per user
    spam_df = df[df['Model_Label'] == 0].copy()
    hijacker_stats = spam_df.groupby('Username').agg({
        'Model_Label': 'count',
        'Likes': 'sum',
        'Comments': 'sum',
        'Estimated_Reach': 'sum' if 'Estimated_Reach' in df.columns else 'count'
    }).reset_index()
    
    hijacker_stats.columns = ['Username', 'Spam_Posts', 'Total_Likes', 'Total_Comments', 'Total_Reach']
    hijacker_stats['Total_Engagement'] = hijacker_stats['Total_Likes'] + hijacker_stats['Total_Comments']
    
    # Filter for serial hijackers (multiple spam posts)
    serial_hijackers = hijacker_stats[hijacker_stats['Spam_Posts'] >= min_spam_posts]
    serial_hijackers = serial_hijackers.sort_values('Spam_Posts', ascending=False)
    
    # Add threat level
    def get_threat_level(spam_count):
        if spam_count >= 5:
            return "EXTREME"
        elif spam_count >= 3:
            return "HIGH"
        else:
            return "MODERATE"
    
    serial_hijackers['Threat_Level'] = serial_hijackers['Spam_Posts'].apply(get_threat_level)
    
    return serial_hijackers


def calculate_hashtag_performance(df):
    """
    Calculate performance per hashtag with risk levels
    """
    hashtag_stats = df.groupby('Target_Hashtag').agg({
        'Model_Label': ['count', 'sum']
    }).reset_index()
    
    hashtag_stats.columns = ['Hashtag', 'Total_Posts', 'Aligned_Posts']
    hashtag_stats['Misaligned_Posts'] = hashtag_stats['Total_Posts'] - hashtag_stats['Aligned_Posts']
    hashtag_stats['Hijack_Rate'] = ((hashtag_stats['Misaligned_Posts'] / hashtag_stats['Total_Posts']) * 100).round(1)
    hashtag_stats['Brand_Alignment'] = ((hashtag_stats['Aligned_Posts'] / hashtag_stats['Total_Posts']) * 100).round(1)
    
    def calculate_risk(hijack_rate):
        if hijack_rate >= 50:
            return "HIGH RISK"
        elif hijack_rate >= 30:
            return "MEDIUM RISK"
        else:
            return "LOW RISK"
    
    hashtag_stats['Risk_Level'] = hashtag_stats['Hijack_Rate'].apply(calculate_risk)
    hashtag_stats = hashtag_stats.sort_values('Hijack_Rate', ascending=False)
    
    return hashtag_stats


def calculate_engagement_metrics(df):
    """
    Calculate engagement quality metrics
    """
    aligned_df = df[df['Model_Label'] == 1]
    misaligned_df = df[df['Model_Label'] == 0]
    
    aligned_total_engagement = aligned_df['Likes'].sum() + aligned_df['Comments'].sum()
    misaligned_total_engagement = misaligned_df['Likes'].sum() + misaligned_df['Comments'].sum()
    total_engagement = aligned_total_engagement + misaligned_total_engagement
    
    engagement_quality_score = (aligned_total_engagement / total_engagement * 100) if total_engagement > 0 else 0
    
    return {
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


def create_compliance_pie_chart(metrics):
    """
    Create pie chart with orange color scheme
    """
    labels = ['Aligned Posts', 'Hijacked Posts']
    values = [metrics['aligned_posts'], metrics['misaligned_posts']]
    colors = [COLORS['light_orange'], COLORS['orange']]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors, line=dict(color='#ffffff', width=3)),
        hole=0.4,
        textinfo='label+percent',
        textfont=dict(size=16, color='#422006', family='Inter', weight=900),
        rotation=90,
        direction='clockwise'
    )])
    
    fig.update_layout(
        title="Brand Alignment Distribution",
        paper_bgcolor=COLORS['light_bg'],
        plot_bgcolor=COLORS['light_bg'],
        font=dict(color='#422006', family='Inter', size=14, weight=800),
        showlegend=True,
        height=400,
        title_font=dict(size=16, color='#422006', weight=800),
        legend=dict(
            font=dict(size=14, color='#422006', weight=800)
        )
    )
    
    return fig


def create_hashtag_risk_heatmap(hashtag_stats):
    """
    Create heatmap with orange gradient and BOLD labels
    """
    # Color gradient from light orange (safe) to dark orange (dangerous)
    colors = []
    for rate in hashtag_stats['Hijack_Rate']:
        if rate >= 50:
            colors.append('#ea580c')  # Dark orange
        elif rate >= 30:
            colors.append('#fb923c')  # Medium orange
        else:
            colors.append('#fdba74')  # Light orange
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=hashtag_stats['Hashtag'],
        x=hashtag_stats['Hijack_Rate'],
        orientation='h',
        marker_color=colors,
        text=[f"{rate}%" for rate in hashtag_stats['Hijack_Rate']],
        textposition='auto',
        textfont=dict(size=15, color='white', family='Inter', weight=900),
        hovertemplate='<b>%{y}</b><br>Hijack Rate: %{x}%<br><extra></extra>'
    ))
    
    fig.update_layout(
        title="Campaign Integrity Heatmap",
        xaxis_title="Hijack Rate (%)",
        yaxis_title="Hashtag",
        paper_bgcolor=COLORS['light_bg'],
        plot_bgcolor=COLORS['chart_bg'],
        font=dict(color='#422006', family='Inter', size=14, weight=700),
        showlegend=False,
        height=450,
        xaxis=dict(
            range=[0, 100],
            tickfont=dict(size=13, color='#422006', weight=700)
        ),
        yaxis=dict(
            tickfont=dict(size=14, color='#422006', weight=800)
        ),
        title_font=dict(size=16, color='#422006', weight=800)
    )
    
    fig.add_vline(x=50, line_dash="dash", line_color='#ea580c', opacity=0.5, 
                  annotation_text="High Risk", annotation_position="top")
    fig.add_vline(x=30, line_dash="dash", line_color='#fb923c', opacity=0.5,
                  annotation_text="Medium Risk", annotation_position="top")
    
    return fig


def create_engagement_comparison_chart(engagement_stats):
    """
    Create engagement comparison with orange colors
    """
    categories = ['Avg Likes', 'Avg Comments']
    aligned_values = [engagement_stats['aligned_avg_likes'], engagement_stats['aligned_avg_comments']]
    misaligned_values = [engagement_stats['misaligned_avg_likes'], engagement_stats['misaligned_avg_comments']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=categories,
        y=aligned_values,
        name='Aligned Posts',
        marker_color=COLORS['light_orange'],
        text=[f"{v:.1f}" for v in aligned_values],
        textposition='auto',
        textfont=dict(color='#422006', size=13, family='Inter', weight=900)
    ))
    
    fig.add_trace(go.Bar(
        x=categories,
        y=misaligned_values,
        name='Hijacked Posts',
        marker_color=COLORS['orange'],
        text=[f"{v:.1f}" for v in misaligned_values],
        textposition='auto',
        textfont=dict(color='white', size=13, family='Inter', weight=900)
    ))
    
    fig.update_layout(
        title="Engagement Quality Analysis",
        xaxis_title="Metric",
        yaxis_title="Average Count",
        barmode='group',
        paper_bgcolor=COLORS['light_bg'],
        plot_bgcolor=COLORS['chart_bg'],
        font=dict(color='#422006', family='Inter', size=14, weight=700),
        showlegend=True,
        height=400,
        title_font=dict(size=16, color='#422006', weight=800),
        xaxis=dict(
            tickfont=dict(size=14, color='#422006', weight=800),
            title_font=dict(size=14, color='#422006', weight=800)
        ),
        yaxis=dict(
            tickfont=dict(size=13, color='#422006', weight=800),
            title_font=dict(size=14, color='#422006', weight=800)
        )
    )
    
    return fig


def create_post_audit_table(df, top_n=20):
    """
    Create post audit table with username tracking
    """
    audit_df = df.copy()
    audit_df['Status'] = audit_df['Model_Label'].apply(lambda x: 'Aligned' if x == 1 else 'Hijacked')
    audit_df['Engagement_Score'] = audit_df['Likes'] + audit_df['Comments']
    
    audit_df = audit_df.sort_values('Engagement_Score', ascending=False)
    audit_df = audit_df.head(top_n)
    
    columns_to_show = ['Username', 'Target_Hashtag', 'Post_Text', 'Likes', 'Comments', 'Status', 'Engagement_Score']
    
    if 'AI_Confidence' in audit_df.columns:
        columns_to_show.insert(-1, 'AI_Confidence')
    if 'Spam_Reason' in audit_df.columns:
        columns_to_show.append('Spam_Reason')
    
    display_df = audit_df[columns_to_show]
    
    return display_df


if __name__ == "__main__":
    from mock_results import get_mock_model_results
    
    print("=== Testing Stats Module ===\n")
    df = get_mock_model_results()
    
    metrics = calculate_compliance_metrics(df)
    print(f"Brand Alignment Score: {metrics['brand_alignment_score']}%")
    print(f"Hijacking Rate: {metrics['hijacking_rate']}%\n")
    
    serial_hijackers = detect_serial_hijackers(df)
    print("Serial Hijackers Detected:")
    print(serial_hijackers.to_string(index=False))
