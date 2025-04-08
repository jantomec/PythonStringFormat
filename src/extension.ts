// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import { spawnSync } from 'child_process';
import { PythonExtension } from '@vscode/python-extension';


async function getPythonInterpreter(): Promise<string> {
	let pythonExecutable = "python";  // DEFAULT_PYTHON
	const pythonApi: PythonExtension = await PythonExtension.api();
	const environmentPath = pythonApi.environments.getActiveEnvironmentPath();
	const environment = await pythonApi.environments.resolveEnvironment(environmentPath);
	if (environment) {
		pythonExecutable = environment.path;
	}
	return pythonExecutable;
}

function suggestConversionType(input: string): string[] {
	if (input === "f-string") {
		return [
			"str.format(args)",
			"str.format(keywords)"
		];
	} else if (input === "str.format(args)") {
		return [
			"f-string",
			"str.format(keywords)"
		];
	} else if (input === "str.format(keywords)") {
		return [
			"f-string",
			"str.format(args)"
		];
	} else if (input === "str.format(args, keywords)") {
		return [
			"f-string",
			"str.format(args)",
			"str.format(keywords)"
		];
	} else if (input === "str") {
		return ["f-string"];
	} else {
		return [];
	}
}

function convert(context: vscode.ExtensionContext) {
	const editor = vscode.window.activeTextEditor;
	if (!editor) { return; }

	const cursor = editor.selection.active;

	getPythonInterpreter().then((pythonPath) => {
		const stringFinderScriptPath = context.asAbsolutePath('src/string_finder.py');
		const text = editor.document.getText();
		const buffer = Buffer.from(text, 'utf-8');

		const lineno = cursor.line;
		const col_offset = cursor.character;

		const result = spawnSync(
			pythonPath,
			[
				stringFinderScriptPath,
				lineno.toString(),
				col_offset.toString()
			],
			{input: buffer}
		);

		if (result.status !== 0) {
			console.error(`Error: ${result.stderr}`);
			vscode.window.showErrorMessage(`No string was found at the cursor position.`);
			return;
		}

		const string = JSON.parse(result.stdout.toString('utf-8'));

		const start = new vscode.Position(string.start.line, string.start.character);
		const end = new vscode.Position(string.end.line, string.end.character);

		const selection = new vscode.Selection(start, end);
		editor.selection = selection;
		editor.revealRange(selection);

		const conversion_options = suggestConversionType(string.type);
		if (conversion_options.length === 0) {
			console.error(`No conversion options available for type: ${string.type}`);
			return;
		}
		vscode.window.showQuickPick(conversion_options, {
			placeHolder: 'Select conversion ...'
		}).then((selected) => {
			if (!selected) {
				return;
			}

			const converterScriptPath = context.asAbsolutePath('src/converter.py');
			const selectedText = editor.document.getText(selection);
			const buffer = Buffer.from(selectedText, 'utf-8');
			const result = spawnSync(pythonPath,
				[
					converterScriptPath,
					selected
				],
				{input: buffer}
			);

			if (result.status !== 0) {
				console.error(`Error: ${result.stderr}`);
				vscode.window.showErrorMessage(`Error: Could not convert string.`);
				return;
			}

			const new_text = result.stdout.toString('utf-8');

			editor.edit(editBuilder => {
				editBuilder.replace(editor.selection, new_text);
			});
		});
	});
}

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated

	// The command has been defined in the package.json file
	// Now provide the implementation of the command with registerCommand
	// The commandId parameter must match the command field in package.json

	context.subscriptions.push(
		vscode.commands.registerCommand('pythonstringformat.convertFormatString', () => {
			convert(context);
		})
	);

}

// This method is called when your extension is deactivated
export function deactivate() {}
