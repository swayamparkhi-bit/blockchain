import hashlib
import json
import time


class Voter:
    def __init__(self, voter_id: str, name: str):
        self.voter_id = voter_id
        self.name = name
        self.has_voted = False


class Candidate:
    def __init__(self, candidate_id: str, name: str):
        self.candidate_id = candidate_id
        self.name = name


class Block:
    def __init__(self, index: int, timestamp: float, transactions: list, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Generates a SHA-256 hash of the block's contents."""
        block_string = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "transactions": self.transactions,
                "previous_hash": self.previous_hash,
            },
            sort_keys=True,
        )
        return hashlib.sha256(block_string.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []

    def create_genesis_block(self) -> Block:
        """Creates the initial block in the chain."""
        return Block(0, time.time(), [{"info": "Genesis Block - Election Started"}], "0")

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_vote_block(self, voter_id: str, candidate_id: str, candidate_name: str):
        """Records a vote as a transaction and mines/appends a new block immediately."""
        transaction = {
            "voter_id": voter_id,
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        }
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=[transaction],
            previous_hash=self.get_latest_block().hash,
        )
        self.chain.append(new_block)

    def is_chain_valid(self) -> bool:
        """Verifies hash integrity and linkage across all blocks."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Check if the stored hash matches a fresh recalculation
            if current_block.hash != current_block.calculate_hash():
                print(f"[!] Data tampering detected at Block #{current_block.index}!")
                return False

            # Check if the block points to the actual hash of the previous block
            if current_block.previous_hash != previous_block.hash:
                print(f"[!] Broken chain link between Block #{previous_block.index} and Block #{current_block.index}!")
                return False

        return True


class VotingSystem:
    def __init__(self):
        self.blockchain = Blockchain()
        self.voters = {}      # {voter_id: Voter}
        self.candidates = {}  # {candidate_id: Candidate}

    def add_candidate(self):
        print("\n--- Add Candidate ---")
        candidate_id = input("Enter Candidate ID: ").strip()
        if not candidate_id:
            print("Error: Candidate ID cannot be empty.")
            return
        if candidate_id in self.candidates:
            print(f"Error: Candidate ID '{candidate_id}' already exists.")
            return

        name = input("Enter Candidate Name: ").strip()
        if not name:
            print("Error: Candidate Name cannot be empty.")
            return

        self.candidates[candidate_id] = Candidate(candidate_id, name)
        print(f"Success: Candidate '{name}' (ID: {candidate_id}) added.")

    def add_voter(self):
        print("\n--- Add Voter ---")
        voter_id = input("Enter Voter ID: ").strip()
        if not voter_id:
            print("Error: Voter ID cannot be empty.")
            return
        if voter_id in self.voters:
            print(f"Error: Voter ID '{voter_id}' already exists.")
            return

        name = input("Enter Voter Name: ").strip()
        if not name:
            print("Error: Voter Name cannot be empty.")
            return

        self.voters[voter_id] = Voter(voter_id, name)
        print(f"Success: Voter '{name}' (ID: {voter_id}) registered.")

    def cast_vote(self):
        print("\n--- Cast Vote ---")
        if not self.candidates:
            print("Error: No candidates available. Add candidates first.")
            return
        if not self.voters:
            print("Error: No registered voters. Add voters first.")
            return

        voter_id = input("Enter your Voter ID: ").strip()
        if voter_id not in self.voters:
            print("Error: Voter ID not found.")
            return

        voter = self.voters[voter_id]
        if voter.has_voted:
            print(f"Error: Voter '{voter.name}' (ID: {voter_id}) has already voted! Double-voting is not allowed.")
            return

        print("\nAvailable Candidates:")
        for cid, cand in self.candidates.items():
            print(f"  [{cid}] {cand.name}")

        candidate_id = input("Enter Candidate ID to vote for: ").strip()
        if candidate_id not in self.candidates:
            print("Error: Invalid Candidate ID.")
            return

        selected_candidate = self.candidates[candidate_id]
        self.blockchain.add_vote_block(voter.voter_id, selected_candidate.candidate_id, selected_candidate.name)
        voter.has_voted = True
        print(f"Success: Vote cast by '{voter.name}' for '{selected_candidate.name}' and recorded on the blockchain!")

    def print_blockchain(self):
        print("\n==================== BLOCKCHAIN LEDGER ====================")
        for block in self.blockchain.chain:
            print(f"Block Index   : {block.index}")
            print(f"Timestamp     : {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block.timestamp))}")
            print(f"Transactions  : {json.dumps(block.transactions, indent=2)}")
            print(f"Previous Hash : {block.previous_hash}")
            print(f"Current Hash  : {block.hash}")
            print("-" * 59)

    def validate_chain(self):
        print("\n--- Validating Blockchain ---")
        if self.blockchain.is_chain_valid():
            print("Status: VALID. All blocks and hashes are intact.")
        else:
            print("Status: INVALID. The blockchain has been compromised.")

    def run(self):
        while True:
            print("\n==========================================")
            print("   BLOCKCHAIN VOTING MANAGEMENT SYSTEM")
            print("==========================================")
            print("1. Add Candidate")
            print("2. Add Voter")
            print("3. Cast Vote")
            print("4. Print Blockchain")
            print("5. Validate Chain")
            print("6. Exit")
            print("==========================================")

            choice = input("Select an option (1-6): ").strip()

            if choice == "1":
                self.add_candidate()
            elif choice == "2":
                self.add_voter()
            elif choice == "3":
                self.cast_vote()
            elif choice == "4":
                self.print_blockchain()
            elif choice == "5":
                self.validate_chain()
            elif choice == "6":
                print("Exiting Voting Management System. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    app = VotingSystem()
    app.run()