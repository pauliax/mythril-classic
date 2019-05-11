from mythril.analysis import solver
from mythril.analysis.report import Issue
from mythril.analysis.swc_data import TEST_INPUT_GENERATOR
from mythril.exceptions import UnsatError
from mythril.analysis.modules.base import DetectionModule
from mythril.laser.ethereum.state.global_state import GlobalState
import logging
import json

log = logging.getLogger(__name__)

DESCRIPTION = """
Generates input transactions for tests
"""


class TestGenerator(DetectionModule):
    """Test input generator"""

    def __init__(self):
        super().__init__(
            name="Test Input Generator",
            swc_id=TEST_INPUT_GENERATOR,
            description=DESCRIPTION,
            entrypoint="callback",
            pre_hooks=["RETURN", "STOP", "REVERT"],
        )
        self._json_array = []

    def reset_module(self):
        """
        Resets the module
        :return:
        """
        super().reset_module()
        self._json_array = []

    def execute(self, state: GlobalState):
        """

        :param state:
        :return:
        """
        self._issues.extend(self._analyze_state(state))
        return self.issues

    def _analyze_state(self, state):
        instruction = state.get_current_instruction()
        log.info("Instruction: " + str(instruction))

        # log.info("State: " + str(state))
        # log.info("Constraints: " + str(state.mstate.constraints))

        try:
            transaction_sequence = solver.get_transaction_sequence(
                state,
                state.mstate.constraints,
            )

            transaction_sequence['opcode'] = instruction['opcode']
            # log.info("TXs: " + str(transaction_sequence))

            self._json_array.append(transaction_sequence)
            # log.info("JSON array: " + str(self._json_array))

            contract = state.environment.active_account.contract_name
            # log.info("Contract: " + str(contract))

            result = {}
            result['contract'] = contract
            result['txs'] = self._json_array

            with open('txs.json', 'w') as outfile:
                json.dump(result, outfile)
        except UnsatError:
            log.info("[TEST_GENERATOR] no model found")

        return []


detector = TestGenerator()
