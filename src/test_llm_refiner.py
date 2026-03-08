from safe_llm_refiner import safe_llm_refine_bullet

bullet = "Carried out COTS product analysis (Cost/Benefit, Feasibility)"
job_title = "SAP CS, CRM and Oracle Quotation Business Analyst"
jd_skills = ["SAP", "CRM", "Oracle", "Quotation / Pricing", "Business Analysis"]

final_bullet, trace = safe_llm_refine_bullet(
    bullet=bullet,
    job_title=job_title,
    jd_skills=jd_skills,
)

print("FINAL BULLET:")
print(final_bullet)
print("\nTRACE:")
print(trace)