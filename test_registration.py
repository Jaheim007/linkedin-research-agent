import unittest
from unittest.mock import patch

import research_agent


class RegistrationErrorResponseTest(unittest.TestCase):
    @patch("research_agent.requests.post", side_effect=RuntimeError("internal failure details"))
    def test_registration_error_response_hides_exception_details(self, _post):
        response = research_agent.register_to_orchestrator(
            research_agent.RegisterRequest(orchestrator_url="http://orchestrator")
        )

        self.assertEqual(response["status"], "error")
        self.assertEqual(response["message"], "Unable to register with orchestrator.")
        self.assertNotIn("internal failure details", str(response))


if __name__ == "__main__":
    unittest.main()
