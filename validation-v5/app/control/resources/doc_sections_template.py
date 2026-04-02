#app\control\resources\doc_sections_template.py

DOC_SECTIONS_TEMPLATE = {
    "VP": {
        "section_1": {
            "purpose": (
                "@This Validation Plan (VP) describes the approach to validate [system name] [version] "
                "according to the Computerized Systems Validation SOP (xxxx). It ensures with documented "
                "evidence that, at release, the system works as intended and complies with the regulations "
                "identified in the Initial  Impact Assessment (IIA) [(ref)] and with internal policies and procedures. "
                "The document details the deliverables, roles and responsibilities, acceptance criteria for release of the system, "
                "and procedures to maintain the system’s capabilities and validated state during operations. "
                "It must be approved before implementation in a controlled environment can start.\n\n"
                "The validation process and outcome will be outlined in the Validation Report (VR) to verify that the Acceptance Criteria "
                "(see section 8) have been met and to confirm by formal approval that the system is validated and fit for use, "
                "and ready for release to the users.\n\n"
                "The implementation of the system is managed by the Change Control process (Request For Change or RFC) [(ref)].@"
            )
        },
        "section_2": {
            "scope": (
                "@The scope of this document is the validation of the GxP system [system name] [version]. For a high-level description of the system and its boundaries refer to section 4.@\n"
                "#Specify the validation scope. For example:#\n"
                "#• Is it an implementation, upgrade, does it include migration?#\n"
                "#• Is configuration (GAMP category 4) or coding (GAMP category 5) needed for implementation ?#\n"
                "#• If applicable, list project phases and related validation scope.#\n"
                "#• Which interfaces are in scope of this VP, if any? Provide diagrams in section 4.3.#"
            ),
            "out_of_scope": (
                "#• Describe what will NOT be included in the validation scope. E.g., interfaces, migration, and list activities that are supplier’s responsibility.#"
            )
        },
        "section_3": {
            "roles_and_responsabilities": (
                "@The roles and responsibilities for this system have been defined in the IIA.@ [The table below lists additional roles / role changes.]\n\n"
                "#• Do NOT repeat the roles & responsibilities from the IIA.#\n"
                "#• If deviating from the IIA, add a justification.#\n"
                "#• If additional or project-specific roles and stakeholders, provide the details in below table.#\n\n"
                "@Table : Role | Name & function | Responsibilities | Rationale@"
            )
        },
        "section_4": {
            "system_description": (
                "#Do NOT duplicate but refer to the IIA or other documentation for more detail (if applicable).#\n"

                "4.1 SYSTEM OVERVIEW\n"
                "#• System name per @Computerized Systems Inventory@ (CSI).#\n"
                "#• Is the system in-house developed, is it a XaaS, who is the supplier?#\n"
                "#• If cloud-based, is it hosted on premises or by the XaaS supplier and who is the cloud provider?#\n"
                "#• Software version/release number, service pack number.#\n"
                "#• Mention the infrastructure supporting or dedicated to the system.#\n"
                "#• System modules and/or sub-systems (e.g., in case of an ERP package).#\n"
                "#• Interfaces to other systems and if these interfaces are in scope.#\n\n"

                "4.2 BUSINESS PROCESS\n"
                "#• High-level purpose and intended use of the system.#\n"
                "#• Who are the end users, global or local?#\n"
                "#• Role-based permissions that will be configured in the system, including administrators and any supplier accounts pre- and post-release (e.g., for service and maintenance).#\n\n"

                "4.3 SYSTEM ARCHITECTURE\n"
                "@The diagram below gives a high-level overview of the system architecture.@\n"
                "#• Insert a system architecture diagram here.#\n"
                "#• Explain the interfaces: are these bi-directional or unidirectional, call/response interactions, or transferring data?#\n\n"

                "4.4 TECHNICAL ENVIRONMENTS\n"
                "#Describe the available technical environments for the system in scope and the purpose of the environments. Select the appropriate text and adjust as needed.#\n"
                "@The system will be available in the following environment(s). Refer to the Glossary and the CSV SOP for planned in [this/these] environment(s):@\n"
                "#• Development environment (qualified/not qualified)#\n"
                "#• Validation environment (qualified)#\n"
                "#• Migration environment (qualified/not qualified)#\n"
                "#• Production environment#\n\n"
                "@definitions and explanations. See section 5.9 [and section 5.8 (Migration)] for the testing activities @"
            )
        },
        "section_5": {
            "validation_strategy": (
                "@The Validation Strategy for [system name] [version] is risk-based according to the outcome of the IIA, Vendor Assessment (VA), Risk Assessment. The strategy is aligned with the CSV SOP and requires the production of the deliverables explained in this section. For an overview see table in section 5.12. More detail can be found in the CSV SOP.@\n\n"
                "#• Explain if deliverables will be combined and if deliverables additional to what is required per CSV SOP will be provided.#\n"
                "#• List available deliverables in section References of this VP.#\n"
                "#• List deliverables that will be leveraged from supplier or implementation partner.#\n"
                "#• Explain how leveraged documentation will be managed if not as per CSV SOP.#\n"
                "#• Note that QMS is the location to store and manage GxP documents. For training deliverables, this is the internal Learning Management System (LMS).#\n"
                "#• If deviating from the CSV SOP, add the justification in this section.#\n"
                "#• If a change occurs during project execution, describe this in the VR. If the change has a GxP impact, update this VP.#"

                "5.1 COMPUTERIZED SYSTEM IMPACT ASSESSMENT\n"
                "@The conclusion of the IIA is that [system name] [version] must be validated and falls in GAMP5® categor[y/ies] [3, and/or 4, and/or 5]. Refer to the IIA for the regulations that apply and the system description. "
                "The IIA must be approved before approval of this VP.@"

                "5.2 VENDOR ASSESSMENT\n"
                "@The [Vendor Assessment/Audit] has been conducted for [supplier name(s) X, and Y, and Z] as per.@\n"
                "#• If an audit, it suffices to reference the Audit Report and no need to refer the audit SOP.#\n"
                "@The Report(s) stating the [VA/Audit] outcome must be approved before approval of this VP.@\n"
                "#• If applicable, summarize the outcome, observations and planned actions defined in the Report (see section Conclusion) and explain the impact on the validation approach.#"

                "5.3 USER REQUIREMENTS DOCUMENT\n"
                "@The User Requirements Document(s) (URS) [(ref)] will provide(s) the required information about the business process and the requested supporting system functionalities. The URS serves as the basis for the development of the functional and/or configuration specifications, as applicable, and for User Acceptance Testing (UAT) (see 5.9).\n"
                "The URS(s) must be approved before Risk Assessment can start, before implementation in the Validation environment, and before approval of Testing deliverables. The URS(s) must be maintained throughout the system lifecycle.@"

                "5.4 FUNCTIONAL AND CONFIGURATION SPECIFICATIONS\n"
                "@The Functional Specifications (FS) document(s) [(ref)] will describe the requested behavior of the system from a technical point of view. Each requirement in the URS(s) must be implemented by one or more functional specifications.#\n"
                "@The Configuration Specifications (CS) document(s) [(ref)] will list the settings and parameters needed to implement the system as required by the business.#\n"
                "@The FS and CS must be approved before Functional Testing and Configuration Testing can start and must be maintained throughout the system lifecycle.@\n"
                "#• FS and CS are required for systems (system components) assessed GAMP5® cat. 4 and 5.#"

                "5.5 DESIGN SPECIFICATIONS\n"
                "@The Design Specifications (DS) document(s) are a further extension of Functional Specifications and a technical answer to the defined requirements and specifications for the system in scope. It will contain sufficient detail to enable the system to be built and maintained and include information on the overall system architecture, coding language, interfaces, screen designs, output format, data flow, algorithms, and graphics.#\n"
                "@The DS must be approved before Code Review can start and must be maintained throughout the system lifecycle.@\n"
                "#• DS is required for GAMP5® category 5 systems (or system components).#"

                "5.6 CODE REVIEW\n"
                "@Source Code Review will ensure that the coding standards defined for the system are consistently and correctly applied, that the code is maintainable, and written in accordance with the design specifications. The extent of the review will be risk based and conducted according to a documented procedure by an independent SME together with the author of the code.#\n"
                "@The Code Review must be approved before formal testing can start.@\n"
                "#• Code Review is required for GAMP5® category 5 systems (or system components).#\n"
                "#• Describe the risk-based review, e.g., if it will be performed on a sample basis or if all code will be reviewed, and how the review will be documented.#\n"
                "#• Add: if the Code Review will be done by an automated source code review tool and how the tool has been qualified.#"

                "5.7 RISK ASSESSMENT\n"
                "@A Risk Assessment (RA) will be performed based on the approved URS to identify and assess GxP and business risks posed by [system name] [version]. The outcome of the RA is input to the validation strategy (this section) and the testing strategy (see section 5.9). Mitigation actions, e.g., more rigorous testing, will be defined in the Test Plan. The risks will be reassessed after mitigation to determine if the risk scores have been reduced to a level acceptable to the Business Owner. The results of the initial RA will be documented in the Risk Assessment Report and the post-mitigation RA will be documented in an update of the RA Report [(ref)].#\n"
                "@The RA Report must be approved before approval of the Test Plan and be maintained throughout the system lifecycle.@\n"
                "#• If the RA is not yet available when authoring the VP, which is usually the case, summarize the RA outcome and explain the impact on the validation strategy in the Test Plan.#\n"
                "#• Project risks are not part of the risk assessment in validation.#"

                "5.8 DATA MIGRATION\n"
                "#• Explain high-level if Data Migration (DM) will be needed and if Data Migration Plan (DMP) and Report (DMR) will be separate deliverables or integrated in the Validation Plan and Report and, for testing activities, Test Plan and Report. Define purpose, scope: the data to migrate, roles & responsibilities, risks and mitigation, data migration strategy, and the testing approach including the environments used (unqualified/qualified pre-Production and qualified Production).#\n"
                "#• The DMP must be approved before data migration activities can start.#\n"
                "#• The DM requirements must be approved before approval of DM test scripts.#\n"
                "#• The DM Tests Scripts must be approved before executing them.#\n"
                "#• The DM Test Plan must be approved before testing can start.#\n"
                "#• The DM Report can only be approved after all DM activities have completed and approved.#"

                "5.9 TESTING\n"
                "@Formal testing will be executed in the Validation environment as per the approved Test Plan(s) (TP). The Test Plan(s) will describe the test approach, i.e., roles & responsibilities, activities and prerequisites, test environment(s), deliverables, and acceptance criteria per test level. The Plan will also clarify if activities and deliverables will be combined, what will be leveraged from supplier, and justify where it is not possible to adhere to the CSV SOP. The Test Report(s) (TR) will summarize the test results and status of defects and verify if the required testing was executed.#\n"
                "@The Test Plan must be approved before formal testing can start.#\n"
                "#• Test Scripts must be approved before execution.#\n"
                "#• Executed scripts, Test Evidence, Defect Forms must be approved before Test Report approval.#\n"
                "#• The Test Report must be approved before approval of the Validation Report.#\n"
                "#• Test Plan and Report can be documented in the VP (this document) and VR respectively. In that case, add the expected content of the Test Plan into this section.#\n"
                "#• Test levels in validation scope depend on the system categorization, e.g., for a system assessed as GAMP Category 3, Functional Testing (OQ) is not required. See CSV SOP.#\n"
                "#• If Functional Testing (also known as OQ) and Requirement Testing (also known as PQ or UAT) activities will be combined, explain that this will be ‘at risk’, meaning that previously approved tests may need to be re-executed as part of defect handling.#\n"
                "#• If applicable, add that the Plan will justify testing activities conducted in other environments. Similarly, justify if a Validation environment will not be used/available, which is exceptionally the case.#\n"
                "#• Installation and configuration specifications typically come from supplier and may be supplemented by local or global requirements.#\n"
                "#• For in-house built applications and single-tenant SaaS, the IQ Report must be approved before other formal testing can start.#\n"
                "#• In case of multitenant SaaS, supplier is the responsible for IQ and provisions a one-for-all qualified environment to all customers.#\n"
                "#• At minimum, the Validation and Production environment will be qualified. Sometimes a qualified Migration environment as well.#\n"
                "#• Exceptionally, the system will be directly installed in Production environment. The rationale for this exception must be defined in the Test Plan.#"

                "5.10 TRACEABILITY MATRIX\n"
                "@The Traceability Matrix (TM) documents the relationship between business requirements [and technical specifications,] and the test scripts or procedures covering these.#\n"
                "@The TM must be approved prior to the approval of the VR and be maintained throughout the system lifecycle when requirements, specifications, and test scripts are updated.@"

                "5.11 VALIDATION REPORT\n"
                "The Validation Report (VR) summarizes the completed validation activities and verifies if all deliverables were produced according to plan (i.e., this Validation Plan, [Data Migration Plan,] Test Plan). The report will conclude whether the acceptance criteria have been met and the computerized system can be released for operational use in the Production environment."
            
                "5.12 VALIDATION DELIVERABLES OVERVIEW\n"
                "The table below lists the planned validation deliverables. In green are the lifecycle deliverables, also known as living documents or evergreen documents, that must be kept up to date throughout the lifecycle of the system, from project over operations to retirement.\n"
                "For roles and responsibilities see CSV SOP.\n"
                "#• Suggestions in blue italic. Select the deliverables and add cell content per this VP.#\n"
                "#• Generate placeholders to be able to include the QMS ID of all planned deliverables.#\n"
                "#• Populate Author and Approvers with roles, not names.#\n"
                "#• Author role can be: Supplier/(Implementation) Partner/Business/Validation SME /QA.#\n"
                "#• Approver roles must be according to the CSV SOP. Note that this SOP allows for some flexibility in selecting the actual approvers.#\n"
                "#• Prerequisites are typically the prior approval of certain deliverables.#"
                "@Table : Deliverable | Reference | Prerequisite(s) | Author | Approver(s)@"
            )
        },
        "section_6": {
            "procedural_documents_and_training": (
                "@The system must remain in a validated state once it has been released for Production use. To this end, system operational lifecycle processes must be in place, for details see CSV SOP and for IDs see below table.@\n"
                "@The following business and system-specific procedural documents will be in a training-ready state, minimum of 3 weeks prior to the release date of [system name] [version]. The documents will be effective at system release. For expectations, roles & responsibilities, see CSV SOP.@\n"
                "#• Suggestions in blue italic. Remove or add as applicable.#\n"
                "#• Generate placeholders to be able to include the QMS reference of all planned deliverables.#\n"
                "@Table : Operational Process | General Procedure Title | Reference | Version@"
                "@Table : Operational Process | System-specific Procedure Title | Reference | Version@"
                "@Users will be trained in these procedures according to their specific needs before they are granted access.@\n"
                "#Describe how training is organized, controlled, documented, and stored. If applicable, refer to a separate Training Plan document. At minimum:#\n"
                "#o Training curriculum and material (e.g., SOPs, etc...).#\n"
                "#o Training Evidence records and where these are stored (LMS is preferred).#\n"
                "#o Target audience (including users, consultants, etc...).#"
            )
        },
        "section_7": {
            "release_approach": (
                "#• Explain if there will be, e.g., a technical release prior to operational release and how this will be managed (e.g., how documentation for each release will be delivered).#\n"
                "#• Explain if a Cutover Plan will be used and/or a rollback plan.#\n"
                "#• Explain risks that may occur at release.#\n"
                "#• Explain how the Handover document will be authored, mutually approved, and shared.#\n"
                "#• Explain how planning of training, verification of training evidence, and granting access is coordinated.#\n"
                "#• Explain how operational release will be communicated, by whom and to whom.#"
            )
        },
        "section_10": {
            "references": (
                "#• Suggestions in blue italic. Remove or add as applicable.#\n"
                "@Table : Related Validation | Quality Documents@\n"
            )
        }
    }
}