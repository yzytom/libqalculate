file(READ "${INPUT_FILE}" CONTENT)
# Escape backslashes
string(REPLACE "\\" "\\\\" CONTENT "${CONTENT}")
# Escape double quotes
string(REPLACE "\"" "\\\"" CONTENT "${CONTENT}")
# Escape newlines
string(REPLACE "\n" "\\n" CONTENT "${CONTENT}")
# Remove carriage returns
string(REPLACE "\r" "" CONTENT "${CONTENT}")

set(DEFINITION "const char * ${VAR_NAME} = \"${CONTENT}\";\n\n")
file(APPEND "${OUTPUT_FILE}" "${DEFINITION}")
