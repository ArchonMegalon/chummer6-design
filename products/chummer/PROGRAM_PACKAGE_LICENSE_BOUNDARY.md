# Program package license boundary

## Purpose

This is static engineering policy. It classifies package ownership and the
license metadata that must be present in produced packages. It does not report
current release availability and it does not replace legal review.

## Canonical matrix

| Owner repository | Surface | Package families | Required package metadata | Repository authority |
| --- | --- | --- | --- | --- |
| `chummer6-core` | rules engine and engine contracts | `Chummer.Engine.Contracts` and any future Core-owned distributable package | `PackageLicenseExpression=GPL-3.0-only` | repository `LICENSE` |
| `chummer6-ui` | desktop, browser, and workbench UI | UI-owned distributable applications or packages | `PackageLicenseExpression=GPL-3.0-only` or an exact packed GPL license file | repository `LICENSE` |
| `chummer6-ui-kit` | shared visual tokens, shell primitives, and reusable UI components | `Chummer.Ui.Kit` | `PackageLicenseExpression=GPL-3.0-only` | package project plus repository policy |
| `chummer6-hub` | hosted orchestration and Hub-owned contracts | `Chummer.Run.Contracts`, `Chummer.Play.Contracts`, `Chummer.Campaign.Contracts`, `Chummer.Control.Contracts`, `Chummer.World.Contracts`, and other Hub-owned packages | `PackageLicenseFile=LICENSE`; the file must be packed unchanged | repository `LICENSE` (`Chummer6 Hub License`, all rights reserved) |
| `chummer6-hub-registry` | Registry contracts and Registry runtime | `Chummer.Hub.Registry.Contracts`, `Chummer.Run.Registry`, and other Registry-owned packages | `PackageLicenseFile=LICENSE`; the file must be packed unchanged | repository `LICENSE` (`Chummer6 Hub License`, all rights reserved) |

## Enforcement

Every packable project must declare exactly one license mechanism. The emitted
NuGet package must contain metadata matching this matrix; a project-file claim
without matching package output is insufficient.

Package-plane locks bind package identity, version, owner repository, exact
source commit, and package digest. A package copied from an ambient cache or
rebuilt from a dirty checkout cannot inherit authority merely because its ID,
version, or license text looks correct.

GPL and proprietary ownership remain explicit across the package boundary.
The matrix does not assert that every possible linking, redistribution, or
combined-distribution arrangement is legally permitted. Any external
distribution that combines those surfaces requires a separate legal and
release review; CI verifies declared provenance and metadata, not legal advice.

Mobile and Media Factory may consume package contracts, but their own
repository or package license must be declared by their owners before they
publish a distributable package. Consumption alone does not copy the license
classification of the dependency onto the consumer repository.
