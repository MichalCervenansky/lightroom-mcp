-- run_tests.lua
-- Simple script to run all tests in the tests directory

local lfs_ok, lfs = pcall(require, "lfs")

local function run_file(file)
    print("----------------------------------------------------------------")
    print("Executing " .. file)
    print("----------------------------------------------------------------")
    local status, err = pcall(dofile, file)
    if not status then
        print("ERROR executing " .. file .. ": " .. tostring(err))
        return false
    end
    return true
end

-- If LuaFileSystem is available, iterate directory, otherwise just run known tests
local files = {
    "TestCommandHandlers.lua"
}

local success = true

for _, file in ipairs(files) do
    if not run_file(file) then
        success = false
    end
end

if not success then
    os.exit(1)
end
