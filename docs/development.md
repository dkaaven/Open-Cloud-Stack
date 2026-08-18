# Development

Cloud Stack development follows the repository contracts defined in `docs/`.

## Adding a module

1. Create `modules/<category>/<module>/`.
2. Add `module.yaml`.
3. Add `README.md`.
4. Add only required directories such as `quadlet/`, `config/`, `health/` or `backup/`.
5. Declare dependencies in `module.yaml`.
6. Validate the module against the schema.
7. Add tests where applicable.

## Changes

* Follow existing templates and schemas.
* Keep module-specific logic inside the module.
* Keep shared policy in `defaults/`.
* Do not commit secrets or deployment-specific data.
* Add an ADR when changing an architectural decision.

## Validation

Changes should verify:

* manifests are valid
* referenced modules exist
* referenced files exist
* profiles resolve correctly
* tests pass
