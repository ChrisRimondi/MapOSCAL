import json

class ProfileControlExtractor:
    def __init__(self, catalog_path, profile_path):
        with open(catalog_path, 'r') as f:
            self.catalog = json.load(f)

        with open(profile_path, 'r') as f:
            self.profile = json.load(f)

        self.catalog_controls = self._index_catalog_controls()
        self.profile_params = self._index_profile_parameters()

    def _index_catalog_controls(self):
        controls = {}

        # Top-level controls (e.g., sc-12)
        for control in self.catalog['catalog'].get('controls', []):
            controls[control['id']] = control

        # Grouped controls
        for group in self.catalog['catalog'].get('groups', []):
            for control in group.get('controls', []):
                controls[control['id']] = control

        return controls

    def _index_profile_parameters(self):
        modify = self.profile['profile'].get('modify', {})
        tailored_params = modify.get('set-parameters', [])
        return {p['param-id']: p for p in tailored_params}

    def _extract_statement_prose(self, control):
        def recurse_parts(parts):
            prose = []
            for part in parts:
                if 'prose' in part:
                    prose.append(part['prose'])
                if 'parts' in part:
                    prose.extend(recurse_parts(part['parts']))
            return prose

        for part in control.get('parts', []):
            if part.get('name') == 'statement':
                prose_output = []
                # ✅ Support for flat or nested prose
                if 'prose' in part:
                    prose_output.append(part['prose'])
                if 'parts' in part:
                    prose_output.extend(recurse_parts(part['parts']))
                return prose_output
        return []

    def extract_control_parameters(self, control_id):
        control = self.catalog_controls.get(control_id)
        if not control:
            return None

        output = {
            "id": control_id,
            "title": control.get("title"),
            "statement": self._extract_statement_prose(control),
            "params": []
        }

        for param in control.get('params', []):
            param_id = param['id']
            tailored = self.profile_params.get(param_id)
            resolved_values = []

            # Tailored values from profile
            if tailored:
                if 'constraints' in tailored:
                    for constraint in tailored['constraints']:
                        desc = constraint.get('description')
                        if desc:
                            resolved_values.append(desc)
                if 'value' in tailored:
                    resolved_values.append(tailored['value'])
                if 'values' in tailored:
                    resolved_values.extend(tailored['values'])

            # Default prose from catalog param definition
            prose_list = []
            if 'guidelines' in param:
                prose_list.extend(g['prose'] for g in param['guidelines'] if 'prose' in g)
            if 'prose' in param:
                prose_list.append(param['prose'])

            output['params'].append({
                "id": param_id,
                "label": param.get("label", ""),
                "resolved-values": resolved_values,
                "prose": prose_list
            })

        return output


if __name__ == "__main__":
    extractor = ProfileControlExtractor(
        catalog_path="../../examples/NIST_SP-800-53_rev5_catalog.json",
        profile_path="../../examples/FedRAMP_rev5_HIGH-baseline_profile.json"
    )
    result = extractor.extract_control_parameters("sc-12")
    print(json.dumps(result, indent=2))
