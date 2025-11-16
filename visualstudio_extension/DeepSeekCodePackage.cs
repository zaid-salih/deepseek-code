// deepseek-code/visualstudio_extension/DeepSeekCodePackage.cs
using System;
using System.Diagnostics;
using System.Globalization;
using System.Runtime.InteropServices;
using System.ComponentModel.Design;
using Microsoft.Win32;
using Microsoft.VisualStudio;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using Microsoft.VisualStudio.OLE.Interop;
using Microsoft.VisualStudio.Shell;
using Task = System.Threading.Tasks.Task;

namespace DeepSeekCode
{
    [PackageRegistration(UseManagedResourcesOnly = true, AllowsBackgroundLoading = true)]
    [InstalledProductRegistration("#110", "#112", "1.0", IconResourceID = 400)]
    [ProvideMenuResource("Menus.ctmenu", 1)]
    [Guid(DeepSeekCodePackage.PackageGuidString)]
    [ProvideAutoLoad(UIContextGuids80.SolutionExists, PackageAutoLoadFlags.BackgroundLoad)]
    public sealed class DeepSeekCodePackage : AsyncPackage
    {
        public const string PackageGuidString = "a8b34b1f-7a2d-4e8a-9c3d-1e2f3a4b5c6d";

        public DeepSeekCodePackage()
        {
        }

        protected override async Task InitializeAsync(CancellationToken cancellationToken, IProgress<ServiceProgressData> progress)
        {
            await this.JoinableTaskFactory.SwitchToMainThreadAsync(cancellationToken);
            await DeepSeekChatCommand.InitializeAsync(this);
            await DeepSeekAnalyzeCommand.InitializeAsync(this);
            await DeepSeekRefactorCommand.InitializeAsync(this);
        }
    }
}