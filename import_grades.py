from pyscript import document, fetch, window, ffi
import csv
import io


async def run(event):
    error = document.querySelector("#error")
    cross_ref_file_input = document.querySelector("#cross-ref-file")
    import_grades_source_input = document.querySelector("#import-grades-source")

    if len(cross_ref_file_input.files) <= 0 and len(import_grades_source_input.files) <= 0:
        error.innerText = "Missing files!"
        return

    cross_ref_file_file = window.URL.createObjectURL(cross_ref_file_input.files.item(0))
    import_grades_source_file = window.URL.createObjectURL(import_grades_source_input.files.item(0))

    cross_ref_file = csv.DictReader(io.StringIO(await fetch(cross_ref_file_file).text()))
    import_grades_source = csv.DictReader(io.StringIO(await fetch(import_grades_source_file).text()))

    output = io.StringIO()
    writer = csv.DictWriter(output, [
        "Unique User ID",
        "PowerSchool_ID",
        "Building ID",
        "Building Title",
        "First Name",
        "Last Name",
        "Email",
        "Position/Job Title",
        "Role",
        "Course Name",
        "Course Code",
        "Department Code",
        "Section Name",
        "Section Code",
        "Section School Code",
        "SIS Section School Code",
        "Grading Period",
        "Titles",
        "Due Dates",
        "Max Points",
        "Grades",
        "Letter Grades",
        "Comments",
        "Exception",
        "Count in Grade",
        "Collected"
    ])

    cross_ref_lookup = {}

    for row in cross_ref_file:
        student_number = row["Student_Number"]
        email = row["U_StudentInfo.ShalhevetEmail"].lower()
        cross_ref_lookup[email] = student_number

    writer.writeheader()
    for row in import_grades_source:
        email = row["Email"].lower()

        psid = "ERROR"
        if email in cross_ref_lookup:
            psid = cross_ref_lookup[email]

        row["PowerSchool_ID"] = psid
        writer.writerow(row)
        pass

    window.URL.revokeObjectURL(cross_ref_file_file)
    window.URL.revokeObjectURL(import_grades_source_file)

    # Most of this is copied from https://docs.pyscript.net/2024.6.1/faq/#download
    data = output.getvalue()
    name = "Grades"
    details = ffi.to_js({"type": "text/csv"})

    file = window.File.new([data], name, details)
    tmp = window.URL.createObjectURL(file)
    dest = document.createElement("a")
    dest.setAttribute("download", name)
    dest.setAttribute("href", tmp)
    dest.click()


