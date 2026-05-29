from __future__ import annotations

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Player(Base):
    __tablename__ = "players"
    player_id = Column(Text, primary_key=True)
    player_name = Column(Text, nullable=False)
    team = Column(Text, nullable=False)
    position = Column(Text, nullable=False)


class AthleteSession(Base):
    __tablename__ = "athlete_sessions"
    session_id = Column(Integer, primary_key=True)
    player_id = Column(Text, ForeignKey("players.player_id"), nullable=False)
    date = Column(Date, nullable=False)
    session_type = Column(Text, nullable=False)
    workload_score = Column(Numeric)
    sprint_count = Column(Integer)
    throwing_volume = Column(Integer)
    pitch_count = Column(Integer)
    average_heart_rate = Column(Numeric)
    max_heart_rate = Column(Numeric)
    recovery_score = Column(Numeric)
    sleep_hours = Column(Numeric)
    soreness_rating = Column(Numeric)
    velocity_trend = Column(Numeric)
    readiness_score = Column(Numeric)
    injury_flag = Column(Integer)


class AthleteFeature(Base):
    __tablename__ = "athlete_features"
    feature_id = Column(Integer, primary_key=True)
    player_id = Column(Text, ForeignKey("players.player_id"), nullable=False)
    date = Column(Date, nullable=False)
    workload_7d_avg = Column(Numeric)
    workload_28d_avg = Column(Numeric)
    acwr = Column(Numeric)
    throwing_7d_avg = Column(Numeric)
    sprint_7d_avg = Column(Numeric)
    soreness_7d_avg = Column(Numeric)
    sleep_7d_avg = Column(Numeric)
    recovery_trend = Column(Numeric)
    readiness_trend = Column(Numeric)
    workload_spike_flag = Column(Boolean)
    fatigue_flag = Column(Boolean)
    low_recovery_flag = Column(Boolean)
    high_soreness_flag = Column(Boolean)
    fatigue_status = Column(Text)


class InjuryRiskScore(Base):
    __tablename__ = "injury_risk_scores"
    risk_id = Column(Integer, primary_key=True)
    player_id = Column(Text, ForeignKey("players.player_id"), nullable=False)
    date = Column(Date, nullable=False)
    injury_risk_score = Column(Numeric, nullable=False)
    risk_category = Column(Text, nullable=False)
    model_version = Column(Text, nullable=False)
