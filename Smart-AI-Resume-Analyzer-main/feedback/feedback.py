import streamlit as st
import sqlite3
import time
import pandas as pd
from datetime import datetime


class FeedbackManager:
    def __init__(self):
        self.db_path = "/tmp/feedback.db"
        self.setup_database()

    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rating INTEGER,
            usability_score INTEGER,
            feature_satisfaction INTEGER,
            missing_features TEXT,
            improvement_suggestions TEXT,
            user_experience TEXT,
            timestamp TIMESTAMP
        )
        """)

        conn.commit()
        conn.close()

    def save_feedback(self, feedback_data):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("""
        INSERT INTO feedback (
            rating, usability_score, feature_satisfaction,
            missing_features, improvement_suggestions,
            user_experience, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            feedback_data.get('rating', 0),
            feedback_data.get('usability_score', 0),
            feedback_data.get('feature_satisfaction', 0),
            feedback_data.get('missing_features', ''),
            feedback_data.get('improvement_suggestions', ''),
            feedback_data.get('user_experience', ''),
            datetime.now()
        ))

        conn.commit()
        conn.close()

    def get_feedback_stats(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM feedback", conn)
        conn.close()

        if df.empty:
            return {
                'avg_rating': 0,
                'avg_usability': 0,
                'avg_satisfaction': 0,
                'total_responses': 0
            }

        return {
            'avg_rating': df['rating'].mean(),
            'avg_usability': df['usability_score'].mean(),
            'avg_satisfaction': df['feature_satisfaction'].mean(),
            'total_responses': len(df)
        }

    def render_feedback_form(self):
        st.markdown("""
            <style>
            @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
            
            .feedback-container {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                padding: 30px;
                border-radius: 20px;
                margin: 20px 0;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            
            .feedback-header {
                color: #E0E0E0;
                font-size: 1.5em;
                font-weight: 600;
                margin-bottom: 25px;
                text-align: center;
                padding: 15px;
                background: linear-gradient(135deg, #4CAF50, #2196F3);
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2);
            }
            
            .feedback-section {
                margin: 20px 0;
                padding: 20px;
                border-radius: 15px;
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.1);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            
            .feedback-section:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }
            
            .feedback-label {
                color: #E0E0E0;
                font-size: 1.1em;
                font-weight: 500;
                margin-bottom: 10px;
            }
            
            .rating-container {
                display: flex;
                align-items: center;
                gap: 10px;
                margin: 15px 0;
            }
            </style>
            """, unsafe_allow_html=True)

        st.markdown('<div class="feedback-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="feedback-header">📝 Share Your Feedback</h2>', unsafe_allow_html=True)

        rating = st.slider("Overall Rating", 1, 5, 5, label_visibility="collapsed")
        usability_score = st.slider("Usability Score", 1, 5, 5, label_visibility="collapsed")
        feature_satisfaction = st.slider("Feature Satisfaction", 1, 5, 5, label_visibility="collapsed")

        missing_features = st.text_area("Missing Features", label_visibility="collapsed")
        improvement_suggestions = st.text_area("Improvement Suggestions", label_visibility="collapsed")
        user_experience = st.text_area("User Experience", label_visibility="collapsed")

        if st.button("Submit Feedback", key="submit_feedback"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i in range(100):
                progress_bar.progress(i + 1)
                time.sleep(0.01)

            feedback_data = {
                'rating': rating,
                'usability_score': usability_score,
                'feature_satisfaction': feature_satisfaction,
                'missing_features': missing_features,
                'improvement_suggestions': improvement_suggestions,
                'user_experience': user_experience
            }

            self.save_feedback(feedback_data)

            progress_bar.empty()
            status_text.empty()

            st.success("🎉 Feedback submitted successfully!")
            st.balloons()

    def render_feedback_stats(self):
        stats = self.get_feedback_stats()

        st.markdown("### 📊 Feedback Overview")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total", stats['total_responses'])
        col2.metric("Rating", f"{stats['avg_rating']:.1f}")
        col3.metric("Usability", f"{stats['avg_usability']:.1f}")
        col4.metric("Satisfaction", f"{stats['avg_satisfaction']:.1f}")
