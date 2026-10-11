"""Pydantic schemas for resume extraction."""
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ContactInformation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None


class WorkExperience(BaseModel):
    model_config = ConfigDict(extra="ignore")
    company: Optional[str] = None
    role: Optional[str] = None
    duration: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)


class Education(BaseModel):
    model_config = ConfigDict(extra="ignore")
    degree: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None


class ResumeData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    contact_information: ContactInformation = Field(default_factory=ContactInformation)
    professional_summary: Optional[str] = None
    work_experience: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    technical_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    extracted_data: ResumeData
    mode: str = "llm"


class ErrorResponse(BaseModel):
    detail: str
