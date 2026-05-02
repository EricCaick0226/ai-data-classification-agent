# Data Classification Report

This report summarizes the classification and risk level of each field in the dataset.

## Summary

- Total fields: 3
- Fields needing manual review: 1
- High or Critical risk fields: 1

## Field Classification Details

| Field Name | Data Type | Missing Count | Category | Risk Level | Reason | Recommendation | Needs Review |
|---|---|---|---|---|---|---|---|
| email | object | 0 | PII | Medium | Email can identify or contact a person. | Protect this field and avoid unnecessary exposure. | False |
| notes | object | 1 | Unknown | Unknown | Free-text fields may contain unpredictable information. | Review this field manually before sharing. | True |
| password | object | 0 | Authentication | Critical | Passwords are sensitive authentication data. | Never expose passwords in plain text. | False |
