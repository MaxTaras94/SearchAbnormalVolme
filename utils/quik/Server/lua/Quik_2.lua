script_path = getScriptPath()
package.path = package.path .. ";" .. script_path .. "\\?.lua;" .. script_path .. "\\?.luac"..";"..".\\?.lua;"..".\\?.luac"
require("QuikSharp")

-- Do not edit this file. Just copy it and save with a different name. Then write required params for it inside config.json file
-- Не редактируйте этой файл. Просто скопируйте и сохраните под другим именем. После этого укажите настройки для него в файле config.json

function main()
    if setup(scriptFilename()) then
        run()
    end
end