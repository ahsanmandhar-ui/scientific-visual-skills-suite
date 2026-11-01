# Long-Term PM2.5 Exposure, Urban Heat Islands, and Incident Adult-Onset Asthma Across 14 Metropolitan Cohorts (2016–2025)

**Study Classification:** POPULATION SURVEILLANCE COHORT · 1.84M PERSON-YEARS · STROBE · SYNTHETIC DATA  
**Authors:** Mateo Alvarez, ScD¹; Amina Darwish, PhD²; Kenji Takahashi, MD, MPH¹  
**Affiliations:** ¹Global Environmental Epidemiology Consortium; ²Center for Satellite Climate Exposure Modeling (Synthetic Demonstration Study)  

## Poster Sections

### timeline_upper_band

- **Rendered Figure Asset:** `epi_timeline.png`

### 01  Public Health Context & Aim

Fine particulate pollution (PM2.5) and urban heat island (UHI) warming co-concentrate in dense metropolitan neighborhoods, amplifying airway oxidative stress [1].

- Objective: Quantify independent and joint associations of chronic PM2.5 and nocturnal UHI intensity with adult-onset asthma across 1.84 million person-years.

### 02  Exposure & Statistical Methods

- Exposures: Ensemble satellite-monitor PM2.5 (μg/m³) and warm-season nocturnal surface temperature anomaly (°C vs. rural buffer).
- Models: Multivariable quasi-Poisson survival models adjusted for age, sex, smoking pack-years, BMI, greenness (NDVI), and neighborhood deprivation index.
- Effect Modification: Relative Excess Risk due to Interaction (RERI) quantified departure from additivity [2].

### Synergistic Air-Heat Respiratory Risk

**Key Quantitative Metric:** `IRR 1.38 in High-Heat Quartile (RERI = 0.21; p = 0.003)`

Overall incidence was 4.84 per 1,000 person-years (8,912 cases). Each +10 μg/m³ PM2.5 increased asthma risk by 24% overall (IRR 1.24, 95% CI 1.18–1.31), rising to 38% in high-UHI neighborhoods.

### 03  Exposure–Response Incidence by Heat Stratum

- **Rendered Figure Asset:** `exposure_curve.png`
- **Caption:** Figure 1. Standardized adult-onset asthma incidence per 1,000 person-years across chronic PM2.5 and nocturnal UHI quartiles.

### 04  Stratified Multivariable Models

| Exposure Stratum | Cases / PY | Adjusted IRR (95% CI) | p-value |
| --- | --- | --- | --- |
| Overall (+10 μg/m³ PM2.5) | 8,912 / 1.84M | 1.24 (1.18–1.31) | 0.0001 |
| Low UHI Q1 (<+0.8°C) | 1,640 / 0.46M | 1.14 (1.07–1.22) | 0.0004 |
| Moderate UHI Q2–Q3 | 4,192 / 0.92M | 1.23 (1.16–1.30) | 0.0001 |
| High UHI Q4 (≥+3.0°C) | 3,080 / 0.46M | 1.38 (1.29–1.48) | 0.0001 |
| Never-smokers sensitivity | 5,410 / 1.19M | 1.26 (1.19–1.34) | 0.0001 |

*Adjusted for age, sex, smoking, BMI, NDVI greenness, and area deprivation.*

### 05  Limitations & Policy Implications

- Limitation: Residential geocoding omits workplace indoor air filtration and transit exposure.
- Policy Action: Co-targeting PM2.5 emissions and urban heat mitigation in high-UHI districts could avert an estimated 19.4% of attributable adult-onset cases.

## References

- [1] Liu C et al. N Engl J Med 2019;381:705–715.
- [2] VanderWeele TJ, Knol MJ. Epidemiol Rev 2014;36:115–147.

## Funding, Disclosures & Correspondence

- Funding: Synthetic Climate-Health Program SYN-EPI-88
- Correspondence: m.alvarez@synthetic-epi.org
- SYNTHETIC DATASET DISCLOSURE: Simulated surveillance cohort for poster skill verification.
