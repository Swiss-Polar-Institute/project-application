#!/bin/bash

# --rule 'indent: "tab"' Disabled, doesn't apply

curlylint --include '\.tmpl' \
	--rule 'html_has_lang: "en"' \
	--rule 'aria_role: true' \
	--rule 'django_forms_rendering: true' \
	--rule 'image_alt: true' \
	--rule 'meta_viewport: true' \
	--rule 'no_autofocus: true' \
	--rule 'tabindex_no_positive: true' \
	ProjectApplication/project_core/templates \
	ProjectApplication/variable_templates/templates \
	ProjectApplication/colours/templates \
	ProjectApplication/comments/templates \
	ProjectApplication/evaluation/templates \
	ProjectApplication/grant_management/templates \
	ProjectApplication/reporting/templates
