// deepseek-code/visualstudio_extension/DeepSeekAnalyzeCommand.cs
using System;
using System.ComponentModel.Design;
using System.Globalization;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using Task = System.Threading.Tasks.Task;

namespace DeepSeekCode
{
    internal sealed class DeepSeekAnalyzeCommand
    {
        public const int CommandId = 0x0101;

        public static readonly Guid CommandSet = new Guid("b8b34b1f-7a2d-4e8a-9c3d-1e2f3a4b5c6e");

        private readonly AsyncPackage package;

        private DeepSeekAnalyzeCommand(AsyncPackage package, OleMenuCommandService commandService)
        {
            this.package = package ?? throw new ArgumentNullException(nameof(package));
            commandService = commandService ?? throw new ArgumentNullException(nameof(commandService));

            var menuCommandID = new CommandID(CommandSet, CommandId);
            var menuItem = new MenuCommand(this.Execute, menuCommandID);
            commandService.AddCommand(menuItem);
        }

        public static DeepSeekAnalyzeCommand Instance
        {
            get;
            private set;
        }

        private Microsoft.VisualStudio.Shell.IAsyncServiceProvider ServiceProvider
        {
            get
            {
                return this.package;
            }
        }

        public static async Task InitializeAsync(AsyncPackage package)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync(package.DisposalToken);

            OleMenuCommandService commandService = await package.GetServiceAsync(typeof(IMenuCommandService)) as OleMenuCommandService;
            Instance = new DeepSeekAnalyzeCommand(package, commandService);
        }

        private void Execute(object sender, EventArgs e)
        {
            ThreadHelper.ThrowIfNotOnUIThread();

            // Get active document
            var doc = GetActiveDocument();
            if (doc != null)
            {
                VsShellUtilities.ShowMessageBox(
                    this.package,
                    $"Would analyze: {doc}",
                    "DeepSeek-Code Analysis",
                    OLEMSGICON.OLEMSGICON_INFO,
                    OLEMSGBUTTON.OLEMSGBUTTON_OK,
                    OLEMSGDEFBUTTON.OLEMSGDEFBUTTON_FIRST);
            }
        }

        private string GetActiveDocument()
        {
            ThreadHelper.ThrowIfNotOnUIThread();

            IVsMonitorSelection monitorSelection = 
                (IVsMonitorSelection)Package.GetGlobalService(typeof(SVsShellMonitorSelection));
            monitorSelection.GetCurrentElementValue(
                (uint)VSSELELEMID.SEID_DocumentFrame, out object frameObj);

            if (frameObj is IVsWindowFrame frame)
            {
                frame.GetProperty((int)__VSFPROPID.VSFPROPID_pszMkDocument, out object pathObj);
                return pathObj as string;
            }

            return null;
        }
    }
}