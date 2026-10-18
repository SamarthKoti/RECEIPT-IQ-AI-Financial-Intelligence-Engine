import ts from "typescript";
import fs from "node:fs";
const config = ts.readConfigFile("tsconfig.json", ts.sys.readFile);
const parsed = ts.parseJsonConfigFileContent(config.config, ts.sys, ".");
const host = {
  getScriptFileNames: () => parsed.fileNames,
  getScriptVersion: () => "0",
  getScriptSnapshot: (name) =>
    fs.existsSync(name)
      ? ts.ScriptSnapshot.fromString(fs.readFileSync(name, "utf8"))
      : undefined,
  getCurrentDirectory: () => process.cwd(),
  getCompilationSettings: () => parsed.options,
  getDefaultLibFileName: (options) => ts.getDefaultLibFilePath(options),
  fileExists: ts.sys.fileExists,
  readFile: ts.sys.readFile,
  readDirectory: ts.sys.readDirectory,
};
const service = ts.createLanguageService(host);
for (const fileName of parsed.fileNames) {
  const changes = service.organizeImports({ type: "file", fileName }, {}, {});
  for (const change of changes) {
    let text = fs.readFileSync(change.fileName, "utf8");
    for (const edit of [...change.textChanges].sort(
      (a, b) => b.span.start - a.span.start,
    )) {
      text =
        text.slice(0, edit.span.start) +
        edit.newText +
        text.slice(edit.span.start + edit.span.length);
    }
    fs.writeFileSync(change.fileName, text);
  }
}
