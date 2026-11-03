# Charte de collaboration

## Nommage des branches

| Préfixe | Usage | Exemple |
|---------|-------|---------|
| feature/ | Nouvelle fonctionnalité | feature/login-page |
| fix/ | Correction de bug | fix/empty-task-title |
| test/ | Tests | test/login-cases |
| docs/ | Documentation | docs/readme-install |
| hotfix/ | Correction urgente | hotfix/payment-error |
| chore/ | Maintenance technique | chore/update-flask |

## Format des messages de commit (Conventional Commits)

Un message de commit suit la forme `type: description courte (#numéro-issue)`.

Les types les plus utilisés sont :

- `feat` : nouvelle fonctionnalité
- `fix` : correction
- `docs` : documentation
- `test` : tests
- `refactor` : réorganisation du code sans changer le comportement
- `chore` : tâches techniques
- `style` : mise en forme

### Exemples

```
feat: add login form (#12)
fix: prevent empty task title (#27)
test: add unit tests for authentication (#13)
docs: explain installation steps in README
```

## Labels utilisés

| Label | Signification |
|-------|---------------|
| `feature` | Nouvelle fonctionnalité demandée |
| `bug` | Comportement incorrect constaté |
| `docs` | Documentation |
| `urgent` | À traiter en priorité |
| `blocked` | Tâche bloquée par une dépendance |
| `ready-for-test` | Développement terminé, prêt pour la validation |
| `tested` | Validé par le testeur |
