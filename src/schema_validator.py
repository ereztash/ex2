"""
Blueprint Schema Validator

This module validates blueprint.json files against the reverse-engineered
Make.com schema (Table 2.1 from architecture spec).

Since Make.com doesn't provide an official JSON Schema file, this validator
implements the formal specification discovered through analysis.

Reference: Section 2 of the architecture spec
"""

from typing import Dict, List, Any, Optional


class BlueprintValidator:
    """
    Validates blueprint.json against Make.com Schema 2.1.

    This validator enforces the schema specification from Table 2.1,
    ensuring generated blueprints will be accepted by Make.com's API.
    """

    def validate(self, blueprint: Dict) -> bool:
        """
        Validate a blueprint against the schema.

        Args:
            blueprint: Blueprint dict to validate

        Returns:
            bool: True if valid

        Raises:
            ValidationError: If blueprint is invalid (with detailed message)

        Example:
            >>> validator = BlueprintValidator()
            >>> validator.validate(my_blueprint)
            True
        """
        errors = []

        # Root level validation
        errors.extend(self._validate_root(blueprint))

        # Flow array validation
        if "flow" in blueprint:
            errors.extend(self._validate_flow(blueprint["flow"]))

        # Metadata validation
        if "metadata" in blueprint:
            errors.extend(self._validate_metadata(blueprint["metadata"]))

        if errors:
            raise ValidationError(
                f"Blueprint validation failed with {len(errors)} error(s):\n" +
                "\n".join(f"  - {e}" for e in errors)
            )

        return True

    def _validate_root(self, blueprint: Dict) -> List[str]:
        """Validate root-level required fields."""
        errors = []

        # Required: name
        if "name" not in blueprint:
            errors.append("Missing required field: 'name'")
        elif not isinstance(blueprint["name"], str):
            errors.append("Field 'name' must be a string")

        # Required: flow
        if "flow" not in blueprint:
            errors.append("Missing required field: 'flow'")
        elif not isinstance(blueprint["flow"], list):
            errors.append("Field 'flow' must be an array")

        # Required: metadata
        if "metadata" not in blueprint:
            errors.append("Missing required field: 'metadata'")

        return errors

    def _validate_flow(self, flow: List[Dict]) -> List[str]:
        """Validate flow array (modules)."""
        errors = []

        if not flow:
            errors.append("Flow array is empty - must contain at least one module")
            return errors

        module_ids = set()

        for idx, module in enumerate(flow):
            # Required: id
            if "id" not in module:
                errors.append(f"Module {idx}: missing required field 'id'")
            else:
                module_id = module["id"]
                if not isinstance(module_id, int):
                    errors.append(f"Module {idx}: 'id' must be an integer")
                elif module_id in module_ids:
                    errors.append(f"Module {idx}: duplicate id {module_id}")
                else:
                    module_ids.add(module_id)

            # Required: module
            if "module" not in module:
                errors.append(f"Module {idx}: missing required field 'module'")
            elif not isinstance(module["module"], str):
                errors.append(f"Module {idx}: 'module' must be a string")

            # Required: version
            if "version" not in module:
                errors.append(f"Module {idx}: missing required field 'version'")
            elif not isinstance(module["version"], int):
                errors.append(f"Module {idx}: 'version' must be an integer")

            # Required: metadata.designer
            if "metadata" not in module:
                errors.append(f"Module {idx}: missing required field 'metadata'")
            elif "designer" not in module["metadata"]:
                errors.append(f"Module {idx}: missing required field 'metadata.designer'")
            else:
                designer = module["metadata"]["designer"]
                if "x" not in designer:
                    errors.append(f"Module {idx}: missing 'metadata.designer.x'")
                if "y" not in designer:
                    errors.append(f"Module {idx}: missing 'metadata.designer.y'")

            # Optional but structured: filter
            if "filter" in module:
                errors.extend(self._validate_filter(module["filter"], idx))

            # Optional but structured: routes (for Router modules)
            if "routes" in module:
                errors.extend(self._validate_routes(module["routes"], idx))

        return errors

    def _validate_metadata(self, metadata: Dict) -> List[str]:
        """Validate metadata.scenario object."""
        errors = []

        if "scenario" not in metadata:
            errors.append("Missing required field: 'metadata.scenario'")
            return errors

        scenario = metadata["scenario"]

        # Required fields in metadata.scenario
        required_fields = {
            "roundtrips": int,
            "maxErrors": int,
            "autoCommit": bool,
            "sequential": bool
        }

        for field, expected_type in required_fields.items():
            if field not in scenario:
                errors.append(f"Missing required field: 'metadata.scenario.{field}'")
            elif not isinstance(scenario[field], expected_type):
                errors.append(
                    f"Field 'metadata.scenario.{field}' must be {expected_type.__name__}"
                )

        return errors

    def _validate_filter(self, filter_obj: Dict, module_idx: int) -> List[str]:
        """Validate filter structure."""
        errors = []

        if "name" not in filter_obj:
            errors.append(f"Module {module_idx}: filter missing 'name'")

        if "conditions" not in filter_obj:
            errors.append(f"Module {module_idx}: filter missing 'conditions'")
        elif not isinstance(filter_obj["conditions"], list):
            errors.append(f"Module {module_idx}: filter.conditions must be an array")
        else:
            # Conditions is array of arrays
            for cond_idx, cond_group in enumerate(filter_obj["conditions"]):
                if not isinstance(cond_group, list):
                    errors.append(
                        f"Module {module_idx}: filter.conditions[{cond_idx}] must be an array"
                    )
                else:
                    # Each condition needs a, b, o
                    for cond in cond_group:
                        if not isinstance(cond, dict):
                            errors.append(
                                f"Module {module_idx}: condition must be an object"
                            )
                        else:
                            if "a" not in cond:
                                errors.append(
                                    f"Module {module_idx}: condition missing 'a'"
                                )
                            if "b" not in cond:
                                errors.append(
                                    f"Module {module_idx}: condition missing 'b'"
                                )
                            if "o" not in cond:
                                errors.append(
                                    f"Module {module_idx}: condition missing 'o' (operator)"
                                )

        return errors

    def _validate_routes(self, routes: List[Dict], module_idx: int) -> List[str]:
        """Validate router routes structure."""
        errors = []

        if not isinstance(routes, list):
            errors.append(f"Module {module_idx}: routes must be an array")
            return errors

        for route_idx, route in enumerate(routes):
            if "flow" not in route:
                errors.append(
                    f"Module {module_idx}: route {route_idx} missing 'flow' array"
                )
            elif not isinstance(route["flow"], list):
                errors.append(
                    f"Module {module_idx}: route {route_idx} 'flow' must be an array"
                )

        return errors


class ValidationError(Exception):
    """Raised when blueprint validation fails."""
    pass
