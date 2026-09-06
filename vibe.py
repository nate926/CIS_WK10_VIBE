"""Student record manager with test scores and calculated letter grades."""

from dataclasses import dataclass, field

MAX_TEST_SCORES = 3
RECORDS_FILE = "student grades txt"


def letter_grade(average: float) -> str:
	"""Return the letter grade for a percentage average."""
	if average >= 90:
		return "A"
	if average >= 80:
		return "B"
	if average >= 70:
		return "C"
	if average >= 60:
		return "D"
	return "F"


@dataclass
class Student:
	"""A student's identifying information and test scores."""

	id: str
	name: str
	scores: list[float] = field(default_factory=list)

	@property
	def student_id(self) -> str:
		"""Return the student's ID using the manager's legacy name."""
		return self.id

	@property
	def average(self) -> float:
		"""Calculate the student's average score."""
		return sum(self.scores) / len(self.scores) if self.scores else 0.0

	@property
	def grade(self) -> str:
		"""Calculate the student's letter grade."""
		return letter_grade(self.average)


class StudentRecordManager:
	"""Store, update, and display student records."""

	def __init__(self) -> None:
		self.students: dict[str, Student] = {}

	def add_student(self, student_id: str, name: str) -> Student:
		if student_id in self.students:
			raise ValueError("A student with that ID already exists.")
		student = Student(id=student_id, name=name)
		self.students[student_id] = student
		return student

	def remove_student(self, student_id: str) -> None:
		if student_id not in self.students:
			raise ValueError("Student not found.")
		del self.students[student_id]

	def get_student(self, student_id: str) -> Student:
		if student_id not in self.students:
			raise ValueError("Student not found.")
		return self.students[student_id]

	def add_score(self, student_id: str, score: float) -> None:
		if not 0 <= score <= 100:
			raise ValueError("Scores must be between 0 and 100.")
		student = self.get_student(student_id)
		if len(student.scores) >= MAX_TEST_SCORES:
			raise ValueError("Each student can have only three test scores.")
		student.scores.append(score)

	def display_students(self) -> None:
		if not self.students:
			print("No student records found.")
			return

		print(f"{'ID':<12}{'Name':<24}{'Scores':<20}{'Average':<10}Grade")
		print("-" * 74)
		for student in self.students.values():
			self._display_student_row(student)

	def display_student(self, student_id: str) -> None:
		"""Display one student's record."""
		student = self.get_student(student_id)
		print(f"{'ID':<12}{'Name':<24}{'Scores':<20}{'Average':<10}Grade")
		print("-" * 74)
		self._display_student_row(student)

	def find_by_name(self, name: str) -> list[Student]:
		"""Find students whose names exactly match, including case."""
		return [student for student in self.students.values() if student.name == name]

	def class_statistics(self) -> tuple[float, float, float]:
		"""Return the highest, lowest, and overall class averages."""
		if not self.students:
			raise ValueError("No student records found.")
		averages = [student.average for student in self.students.values()]
		return max(averages), min(averages), sum(averages) / len(averages)

	def display_statistics(self) -> None:
		highest, lowest, class_average = self.class_statistics()
		print(f"Highest average: {highest:.2f}%")
		print(f"Lowest average:  {lowest:.2f}%")
		print(f"Class average:   {class_average:.2f}%")

	def save(self, filename: str = RECORDS_FILE) -> None:
		"""Save records as name|id|test1|test2|test3|average|grade."""
		with open(filename, "w", encoding="utf-8") as file:
			for student in self.students.values():
				scores = [f"{score:.2f}" for score in student.scores]
				scores.extend([""] * (MAX_TEST_SCORES - len(scores)))
				values = [
					student.name,
					student.student_id,
					*scores,
					f"{student.average:.2f}",
					student.grade,
				]
				file.write("|".join(values) + "\n")

	@classmethod
	def load(cls, filename: str = RECORDS_FILE) -> "StudentRecordManager":
		"""Load records from a file, or start with an empty manager."""
		manager = cls()
		try:
			with open(filename, encoding="utf-8") as file:
				lines = file.readlines()
		except FileNotFoundError:
			return manager
		except OSError as error:
			raise OSError(f"Could not read '{filename}': {error}") from error

		for line_number, line in enumerate(lines, start=1):
			if not line.strip():
				continue
			try:
				name, student_id, test1, test2, test3, _average, _grade = line.rstrip("\n").split("|")
				student = manager.add_student(student_id, name)
				student.scores = [float(score) for score in (test1, test2, test3) if score]
			except (ValueError, TypeError) as error:
				raise ValueError(f"Invalid record on line {line_number} in '{filename}'.") from error
		return manager

	@staticmethod
	def _display_student_row(student: Student) -> None:
		scores = ", ".join(f"{score:.2f}" for score in student.scores) or "None"
		print(
			f"{student.student_id:<12}{student.name:<24}{scores:<20}"
			f"{student.average:>7.2f}%   {student.grade}"
		)


def get_score() -> float:
	"""Read and validate one score from the user."""
	while True:
		try:
			score = float(input("Test score (0-100): "))
			if 0 <= score <= 100:
				return score
		except ValueError:
			pass
		print("Enter a number between 0 and 100.")


def run() -> None:
	try:
		manager = StudentRecordManager.load()
		print(f"Loaded {len(manager.students)} student record(s).")
	except (OSError, ValueError) as error:
		print(f"File warning: {error}")
		print("Starting with an empty student list.")
		manager = StudentRecordManager()

	while True:
		print("\nStudent Record Manager")
		print("1. Add student")
		print("2. Add test score")
		print("3. View all students")
		print("4. View one student")
		print("5. Remove student")
		print("6. Class statistics")
		print("7. Search by student name")
		print("8. Save records")
		print("Press ESC to save and exit.")
		choice = input("Choose an option: ").strip()

		try:
			if choice == "\x1b" or choice.upper() == "ESC":
				manager.save()
				print("Records saved. Goodbye.")
				break
			if choice == "1":
				student_id = input("Student ID: ").strip()
				name = input("Student name: ").strip()
				if not student_id or not name:
					raise ValueError("Student ID and name are required.")
				manager.add_student(student_id, name)
				manager.save()
				print("Student added.")
			elif choice == "2":
				student_id = input("Student ID: ").strip()
				student = manager.get_student(student_id)
				remaining_scores = MAX_TEST_SCORES - len(student.scores)
				if remaining_scores <= 0:
					raise ValueError("This student already has three test scores.")
				for score_number in range(remaining_scores):
					print(f"Enter score {len(student.scores) + 1} of {MAX_TEST_SCORES}.")
					manager.add_score(student_id, get_score())
				manager.save()
				print("Test scores added.")
			elif choice == "3":
				manager.display_students()
			elif choice == "4":
				manager.display_student(input("Student ID: ").strip())
			elif choice == "5":
				manager.remove_student(input("Student ID: ").strip())
				manager.save()
				print("Student removed.")
			elif choice == "6":
				manager.display_statistics()
			elif choice == "7":
				name = input("Student name (case-sensitive): ")
				matches = manager.find_by_name(name)
				if not matches:
					print("No matching student found.")
				else:
					print(f"{'ID':<12}{'Name':<24}{'Scores':<20}{'Average':<10}Grade")
					print("-" * 74)
					for student in matches:
						manager._display_student_row(student)
			elif choice == "8":
				manager.save()
				print(f"Saved {len(manager.students)} student record(s) to '{RECORDS_FILE}'.")
			else:
				print("Choose an option from 1 to 8, or press ESC.")
		except (ValueError, OSError) as error:
			print(f"Unable to complete that action: {error}")


if __name__ == "__main__":
	run()
