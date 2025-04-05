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

function convert(conversion_type: Number, context: vscode.ExtensionContext) {
	// The code you place here will be executed every time your command is executed
	const editor = vscode.window.activeTextEditor;
	if (!editor) { return; }

	const cursor = editor.selection.active;

	getPythonInterpreter().then((pythonPath) => {
		const scriptPath = context.asAbsolutePath('src/converter.py');
		const text = editor.document.getText();
		const buffer = Buffer.from(text, 'utf-8');

		const lineno = cursor.line + 1;
		const colno = cursor.character + 1;

		const result = spawnSync(
			pythonPath,
			[
				scriptPath,
				lineno.toString(),
				colno.toString(),
				conversion_type.toString()
			],
			{
				input: buffer
			}
		);

		if (result.status !== 0) {
			console.error(`Error: ${result.stderr}`);
			vscode.window.showErrorMessage(`Error: ${result.stderr}`);
			return;
		}

		const new_text = result.stdout.toString('utf-8');

		if (new_text === text) {
			vscode.window.showInformationMessage("No formatted string was found at the cursor position.");
			return;
		}

		const fullRange = new vscode.Range(0, 0, editor.document.lineCount, 0);
		editor.edit(editBuilder => {
			editBuilder.replace(fullRange, new_text);
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
		vscode.commands.registerCommand('pythonstringformat.convertFstringToFormat', () => {
			convert(1, context);
		})
	);

	context.subscriptions.push(
		vscode.commands.registerCommand('pythonstringformat.convertFstringToKeywordsFormat', () => {
			convert(2, context);
		})
	);

	context.subscriptions.push(
		vscode.commands.registerCommand('pythonstringformat.convertFormatToFstring', () => {
			convert(3, context);
		})
	);

}

// This method is called when your extension is deactivated
export function deactivate() {}
