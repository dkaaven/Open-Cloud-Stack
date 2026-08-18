# Profiles

Profiles define which modules make up a Cloud Stack installation.

## Location

```text
profiles/<profile>.yaml
```

Example:

```text
profiles/workplace.yaml
```

## Purpose

Profiles express desired capabilities.

Example:

```yaml
schema: 1

id: workplace

modules:
  - workplace/nextcloud
  - workplace/eurooffice
```

## Dependencies

Profiles list only directly selected modules.

Module dependencies are declared in each module's `module.yaml` and resolved separately.

## Rules

* Profiles must not contain deployment-specific secrets.
* Profiles must not duplicate transitive module dependencies.
* Profiles should remain small and declarative.
* Profile manifests must validate against the profile schema.
