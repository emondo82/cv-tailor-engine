from pydantic import BaseModel, Field
from typing import List, Optional


class CandidateProfile(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    career_start: Optional[str] = None
    years_experience: Optional[int] = None


class LanguageSkill(BaseModel):
    language: str
    spoken: Optional[int] = None
    written: Optional[int] = None
    level: Optional[str] = None


class Certification(BaseModel):
    name: str
    provider: Optional[str] = None
    date: Optional[str] = None


class Education(BaseModel):
    degree: str
    field: Optional[str] = None
    institution: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ProjectExperience(BaseModel):
    company: str
    project_name: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    months: Optional[str] = None
    client: Optional[str] = None
    project_size: Optional[str] = None
    project_description: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    domain: Optional[str] = None


class ResumeKnowledgeBase(BaseModel):
    candidate_profile: CandidateProfile
    languages: List[LanguageSkill] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    projects: List[ProjectExperience] = Field(default_factory=list)
    raw_master_resume_summary: Optional[str] = None