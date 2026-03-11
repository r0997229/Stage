#app\data\doc_tables.py

TABLE_META = {
    "VP": {
        "roles": {
            "dynamic": True,
            "order": ["role", "name_and_function", "responsibilities", "rationale"]
        },
        "planned_validation_deliverables": {
            "dynamic": False,
            "order": ["deliverable", "reference", "prerequisites", "author", "approvers"],
            "grouped": True
        },
        "procedures": {
            "dynamic": False,
            "order": ["operational_process", "procedure_title", "reference","version"],
            "grouped": True
        },
        "references": {
            "dynamic": True,
            "max_rows": 12, 
            "order": ["related_validation", "quality_documents"]
        },
    }
}

DOC_TABLES = {
    "VP": {
        "roles": [
            {
                "role": "",
                "name_and_function": "",
                "responsibilities": "",
                "rationale": ""
            }
        ],
        "planned_validation_deliverables": {
            "pre_validation_deliverables": [
                {
                    "deliverable": "@Computerized System Impact Assessment@",
                    "reference": "[REF]",
                    "prerequisites": "#<N/A>/<>#",
                    "author": "[BIS eCompliance]",
                    "approvers": "[Business Owner, QA]"
                },
                {
                    "deliverable": "@Request For Change – Step 1@",
                    "reference": "[Etc. (to be continued in cells below)]",
                    "prerequisites": "@N/A@",
                    "author": "#<Business Owner>/<System Owner>#",
                    "approvers": "[Etc. (to be continued in cells below)]"
                },
                {
                    "deliverable": "#<Vendor Assessment Report>/<>#",
                    "reference": "",
                    "prerequisites": "[CS VA Request, CS Vendor RA, CS Vendor, Quality & Security Questionnaire.]",
                    "author": "#<QA>/<>#",
                    "approvers": ""
                },
                {
                    "deliverable": "#<Vendor Audit Report>/<>#",
                    "reference": "",
                    "prerequisites": "#<N/A>/<>#",
                    "author": "#<QA>/<>#",
                    "approvers": ""
                },
                {
                    "deliverable": "@Validation Plan (this document)@",
                    "reference": "",
                    "prerequisites": "#<Approved IIA>/<>#",
                    "author": "[BIS eCompliance]",
                    "approvers": ""
                },
                {
                    "deliverable": "[Data Migration Plan\n • add ID of VP if included in VP.]",
                    "reference": "",
                    "prerequisites": "#<Approved IIA>/<>#",
                    "author": "#<Supplier>/<>#",
                    "approvers": ""
                },
                {
                    "deliverable": "@Business Requirements Document@",
                    "reference": "",
                    "prerequisites": "#<N/A>/<>#",
                    "author": "#<Business>/<>#",
                    "approvers": ""
                },
                {
                    "deliverable": "[Functional, Configuration, Design Specifications or combined as applicable]",
                    "reference": "",
                    "prerequisites": "[Approved IIA, URS.]",
                    "author": "[Etc. (to be continued in cells below)]",
                    "approvers": ""
                },
            ],
            "validation_execution_deliverables": [
                {
                    "deliverable": "@Risk Assessment Report (pre-mitigation)@",
                    "reference": "",
                    "prerequisites": "#<Approved URS>/<>#",
                    "author": "",
                    "approvers": ""
                },
                {
                    "deliverable": "#<Test Plan>/<Test Plans>#[ • add ID of VP if included in VP.\n • add new row for each separate Test Plan, if applicable.]",
                    "reference": "",
                    "prerequisites": "[Approved URS, RA, Test Scripts.]",
                    "author": "",
                    "approvers": ""
                },
                {
                    "deliverable": "#<Test Script>/<Test Scripts>#",
                    "reference": "@See Test Plan@",
                    "prerequisites": "[Approved URS, RA.]",
                    "author": "",
                    "approvers": ""
                },
                {
                    "deliverable": "#<IQ Report (Validation environment)>/<>#",
                    "reference": "",
                    "prerequisites": "[Executed IQ Test Plan.]",
                    "author": "",
                    "approvers": ""
                },
                {
                    "deliverable": "#<Code Review>/<>#",
                    "reference": "",
                    "prerequisites": "[Approved DS.]",
                    "author": "",
                    "approvers": ""
                },
                {
                    "deliverable": "#<Executed Test Script>/<Executed Test Scripts>#",
                    "reference": "@See Test Report@",
                    "prerequisites": "[Approved Test Script, Test Plan, IQ Report (Validation environment).]",
                    "author": "",
                    "approvers": ""
                },
                {
                    "deliverable": "#<Test Evidence>/<Test Evidences>#",
                    "reference": "@See Test Report@",
                    "prerequisites": "@N/A@",
                    "author": "",
                    "approvers": ""
                },
                {
                    "deliverable": "#<Test Defect>/<Test Defects>#",
                    "reference": "@See Test Report@",
                    "prerequisites": "@N/A@",
                    "author": "",
                    "approvers": ""
                },
                {
                    "deliverable": "@Risk Assessment Report (updated post mitigation)@",
                    "reference": "",
                    "prerequisites": "[Approved Risk Assessment Report (pre-mitigation), Test Report]",
                    "author": "",
                    "approvers": ""
                },
                {
                    "deliverable": "#<Test Report>/<Test Reports>#[ • add ID of VR if included in VR\n • add new row for each separate Test Report]",
                    "reference": "",
                    "prerequisites": "[Approval of all executed Test Scripts, Test Evidence, Test Defects]",
                    "author": "",
                    "approvers": ""
                },
                {
                    "deliverable": "[Data Migration Report\n • add ID of VR if included in VR]",
                    "reference": "",
                    "prerequisites": "[DM execution and approval of all executed DM Test Scripts, Test Evidence, Test Defects]",
                    "author": "",
                    "approvers": ""
                },
                {
                    "deliverable": "@Traceability Matrix@",
                    "reference": "",
                    "prerequisites": "[Approved URS (FS, CS, DS) and Test Scripts]",
                    "author": "",
                    "approvers": ""
                },
                {
                    "deliverable": "[System name | Version | Cutover Plan]",
                    "reference": "",
                    "prerequisites": "#<N/A>/<>#",
                    "author": "",
                    "approvers": ""
                },
                {
                    "deliverable": "[System name | Version | Handover document]",
                    "reference": "",
                    "prerequisites": "#<N/A>/<>#",
                    "author": "",
                    "approvers": ""
                },
                {
                    "deliverable": "@Validation Report@",
                    "reference": "",
                    "prerequisites": "[Approved Test Report, DM Report, Trace Matrix]",
                    "author": "",
                    "approvers": ""
                },
                {
                    "deliverable": "@Request For Change – Step 2@",
                    "reference": "",
                    "prerequisites": "@Approval of above deliverables@",
                    "author": "#<Business Owner>/<System Owner>#",
                    "approvers": ""
                },
            ],
            "production_release_deliverables": [
                {
                    "deliverable": "#<IQ Report (Production environment)>/<>#",
                    "reference": "",
                    "prerequisites": "[Executed IQ Test Plan]",
                    "author": "",
                    "approvers": ""
                },
                {
                    "deliverable": "@Release Communication (informal)@",
                    "reference": "@N/A@",
                    "prerequisites": "[Approved IQ of Production environment, DM execution and verification in Production]",
                    "author": "",
                    "approvers": ""
                },
                {
                    "deliverable": "@Request For Change – Step 3@",
                    "reference": "",
                    "prerequisites": "@Approval of above deliverables@",
                    "author": "#<Business Owner>/<System Owner>#",
                    "approvers": ""
                }
            ]
        },
        "procedures": {
            "general_procedures": [
                {
                    "operational_process": "@Access Management@",
                    "procedure_title": "",
                    "reference": "",
                    "version": ""
                },
                {
                    "operational_process": "@Release Management@",
                    "procedure_title": "",
                    "reference": "",
                    "version": ""
                },
                {
                    "operational_process": "@Backup & Restore@",
                    "procedure_title": "",
                    "reference": "",
                    "version": ""
                },
                {
                    "operational_process": "@IT Change Management@",
                    "procedure_title": "",
                    "reference": "",
                    "version": ""
                },
                {
                    "operational_process": "@Periodic Review@",
                    "procedure_title": "",
                    "reference": "",
                    "version": ""
                }
            ],
            "system_specific_procedures": [
                {
                    "operational_process": "@System Administration & Operational Monitoring@",
                    "procedure_title": "[add: title]",
                    "reference": "",
                    "version": ""
                },
                {
                    "operational_process": "@System Use@",
                    "procedure_title": "[add: title]",
                    "reference": "",
                    "version": ""
                },
                {
                    "operational_process": "#<Business Continuity>/<>#",
                    "procedure_title": "[add: title]",
                    "reference": "",
                    "version": ""
                },
                {
                    "operational_process": "#<Disaster Recovery>/<>#",
                    "procedure_title": "[add: title]",
                    "reference": "",
                    "version": ""
                },
                {
                    "operational_process": "#<Business SOP>/<>#",
                    "procedure_title": "[add: title]",
                    "reference": "",
                    "version": ""
                },
                {
                    "operational_process": "#<Training Material>/<>#",
                    "procedure_title": "[add: title]",
                    "reference": "",
                    "version": ""
                }
            ],
        },
        
        "references": [
            {
                "related_validation": "",
                "quality_documents": ""
            }
        ]
    }
}
