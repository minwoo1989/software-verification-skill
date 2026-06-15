# tests/fixtures/python-layered/src/application/user_service.py
# VIOLATION: cyclomatic complexity > 10
class UserService:
    def process(self, user, action, context, flags):
        if action == "create":
            if user.name:
                if len(user.name) > 2:
                    if context.get("admin"):
                        if flags.get("notify"):
                            if flags.get("audit"):
                                if context.get("region") == "KR":
                                    if flags.get("strict"):
                                        if user.id > 0:
                                            if flags.get("verified"):
                                                return "ok"
        return "fail"
    # complexity = 1 + 10 branches = 11 → triggers violation

    def validate(self, user, rules):
        if not user:
            return False
        if not user.name:
            return False
        if not rules:
            return False
        for rule in rules:
            if rule.get("required") and not getattr(user, rule["field"], None):
                if rule.get("strict"):
                    raise ValueError(rule["field"])
                return False
        return True
