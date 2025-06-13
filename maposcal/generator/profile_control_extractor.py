import json
from pathlib import Path
from typing import Dict, List, Union, Any, Optional


class ProfileControlExtractor:
    """
    Build a {control_id: {...}} dict containing statement prose and parameters
    for each control enumerated in an OSCAL profile.
    """

    # ---------- Public helpers ------------------------------------------------

    def extract(
        self,
        catalog: Union[str, Path, Dict[str, Any]],
        profile: Union[str, Path, Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Parameters
        ----------
        catalog : str | Path | dict
            Path to catalog JSON file *or* a pre-loaded catalog dict.
        profile : str | Path | dict
            Path to profile JSON file *or* a pre-loaded profile dict.

        Returns
        -------
        Dict[str, Dict[str, Any]]
            {
              "ac-1": {
                  "title": "Policy and Procedures",
                  "statements": ["Develop, document, and disseminate …", "..."],
                  "params": [
                      {"id": "ac-1_prm_1", "label": "organization-defined personnel or roles"},
                      ...
                  ]
              },
              ...
            }
        """
        catalog = self._load_json(catalog)
        profile = self._load_json(profile)

        # Build an id ➔ control mapping for fast lookup (includes enhancements).
        controls_index = {}
        for group in catalog["catalog"]["groups"]:
            for ctrl in self._walk_controls(group.get("controls", [])):
                controls_index[ctrl["id"]] = ctrl

        # Collect control IDs from profile
        profile_control_ids = self._profile_control_ids(profile)

        # Assemble output
        result: Dict[str, Dict[str, Any]] = {}
        for cid in profile_control_ids:
            ctrl = controls_index.get(cid)
            if not ctrl:  # enhancement IDs may need dotted match (e.g., ac-2.1)
                ctrl = self._find_enhancement(controls_index, cid)
            if not ctrl:
                continue  # silently skip; you may prefer to log/raise

            result[cid] = {
                "title": ctrl.get("title", ""),
                "statements": self._collect_statements(ctrl),
                "params": self._collect_params(ctrl),
            }

        return result

    # ---------- Private helpers ----------------------------------------------

    @staticmethod
    def _load_json(src: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
        if isinstance(src, (str, Path)):
            with open(src, "r", encoding="utf-8") as f:
                return json.load(f)
        return src  # already a dict

    @staticmethod
    def _walk_controls(controls: List[Dict[str, Any]]):
        """
        Recursive generator over a control plus any nested enhancements.
        """
        for ctrl in controls:
            yield ctrl
            # Enhancements live under a 'controls' key on the base control.
            for sub in ctrl.get("controls", []):
                yield from ProfileControlExtractor._walk_controls([sub])

    @staticmethod
    def _profile_control_ids(profile: Dict[str, Any]) -> List[str]:
        """
        Extract the list of with-ids[] values from profile -> imports -> include-controls.
        """
        ids: List[str] = []
        for imp in profile["profile"].get("imports", []):
            for inc in imp.get("include-controls", []):
                ids.extend(inc.get("with-ids", []))
        return ids

    @staticmethod
    def _collect_params(control: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Return [{'id': 'ac-1_prm_1', 'label': '…'}, …]
        """
        params_out = []
        for prm in control.get("params", []):
            label = prm.get("label") or prm.get("guidelines", [{}])[0].get("prose", "")
            params_out.append({"id": prm["id"], "label": label})
        return params_out

    @staticmethod
    def _collect_statements(control: Dict[str, Any]) -> List[str]:
        """
        Flatten all prose under the control's main 'statement' part.
        """
        statements: List[str] = []

        def walker(part: Dict[str, Any]):
            if "prose" in part:
                statements.append(part["prose"].strip())
            for sub in part.get("parts", []):
                walker(sub)

        for part in control.get("parts", []):
            if part.get("name") == "statement":
                walker(part)
        return statements

    @staticmethod
    def _find_enhancement(index: Dict[str, Any], enhancement_id: str) -> Optional[Dict[str, Any]]:
        """
        Enhancement IDs are dotted (e.g., 'ac-2.1').  If not found directly,
        derive the base control ('ac-2') and search its children.
        """
        if "." not in enhancement_id:
            return None
        base_id = enhancement_id.split(".", 1)[0]
        base_control = index.get(base_id)
        if not base_control:
            return None
        for sub in base_control.get("controls", []):  # enhancements
            if sub["id"] == enhancement_id:
                return sub
        return None


# ------------------- Quick usage example ------------------------------------
if __name__ == "__main__":
    extractor = ProfileControlExtractor()
    controls_dict = extractor.extract(
        "../../examples/NIST_SP-800-53_rev5_catalog.json",
        "../../examples/NIST_SP-800-53_rev5_HIGH-baseline_profile.json",
    )
    # Show one sample control:
    sample_id = "ac-2"
    print(json.dumps({sample_id: controls_dict[sample_id]}, indent=2))
