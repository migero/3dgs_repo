using System;
using System.CodeDom.Compiler;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Runtime.CompilerServices;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Input;
using System.Windows.Markup;
using System.Windows.Media;
using GoPro.Composition;
using GoPro.Instance;
using GoPro.Storage;

namespace GoPro.Dialogs
{
	public class AutoUpdateWindow : Window, INotifyPropertyChanged, IComponentConnector
	{
		private ProgressWindow m_ProgressWindow;

		private AppCenterService.ReleaseDesc m_Release;

		private bool _contentLoaded;

		public uint Size => m_Release.Size;

		public string ReleaseTitle => $"{FileHelper.ApplicationName} - {m_Release.Version} ({Math.Round((double)Size / 1024.0 / 1024.0, 2)}Mb)";

		public string ReleaseNotes => m_Release.Notes;

		private string ReleaseFilePath => FileHelper.GetAutoUpdateFilePath(m_Release.Version);

		public ImageSource ApplicationLogo { get; set; }

		public event PropertyChangedEventHandler PropertyChanged;

		public AutoUpdateWindow(AppCenterService.ReleaseDesc releaseDesc)
		{
			InitializeComponent();
			m_Release = releaseDesc;
			((FrameworkElement)this).set_DataContext((object)this);
			((Window)this).set_ShowInTaskbar(false);
		}

		protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
		{
			this.PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
		}

		private void Window_Loaded(object sender, RoutedEventArgs e)
		{
			VisualHelper.EnableBlur((Window)(object)this);
		}

		private void DownloadButton_Click(object sender, RoutedEventArgs e)
		{
			if (!Directory.Exists(FileHelper.UserDirectory))
			{
				Directory.CreateDirectory(FileHelper.UserDirectory);
			}
			foreach (FileInfo item in new DirectoryInfo(FileHelper.UserDirectory).EnumerateFiles("*.msi"))
			{
				item.Delete();
			}
			AppCenterService.DownloadFileAsync(m_Release.Url, ReleaseFilePath, ReleaseDownloadProgressed, ReleaseDownloadFinished);
			((Window)this).Hide();
			m_ProgressWindow = new ProgressWindow("LOC_WINDOW_PROGRESS_DOWNLOAD_UPDATE", isCancelVisible: true);
			((Window)m_ProgressWindow).set_Owner(((Window)this).get_Owner());
			m_ProgressWindow.Canceled += delegate
			{
				((Window)m_ProgressWindow).Close();
				m_ProgressWindow = null;
			};
			((Window)m_ProgressWindow).ShowDialog();
			((Window)this).Close();
		}

		private void ReleaseDownloadProgressed(long bytes, long totalBytes)
		{
			if (m_ProgressWindow != null)
			{
				m_ProgressWindow.Progress = (uint)((double)bytes / (double)totalBytes * 100.0);
			}
		}

		private void ReleaseDownloadFinished()
		{
			if (m_ProgressWindow != null)
			{
				if (File.Exists(ReleaseFilePath))
				{
					Process.Start(new ProcessStartInfo
					{
						UseShellExecute = false,
						FileName = "msiexec",
						Arguments = $"/i \"{ReleaseFilePath}\" /quiet /qr /norestart"
					})!.WaitForInputIdle();
				}
				((Window)m_ProgressWindow).Close();
				((Window)this).Close();
			}
		}

		private void RemindMeButton_Click(object sender, RoutedEventArgs e)
		{
			((Window)this).Close();
		}

		private void Title_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
		{
			((Window)this).DragMove();
		}

		private void CloseButton_Click(object sender, RoutedEventArgs e)
		{
			((Window)this).Close();
		}

		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		public void InitializeComponent()
		{
			if (!_contentLoaded)
			{
				_contentLoaded = true;
				Uri uri = new Uri("/GoPro.Common;component/dialogs/autoupdatewindow.xaml", UriKind.Relative);
				Application.LoadComponent((object)this, uri);
			}
		}

		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		[EditorBrowsable(EditorBrowsableState.Never)]
		void IComponentConnector.Connect(int connectionId, object target)
		{
			//IL_002b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0035: Expected O, but got Unknown
			//IL_0037: Unknown result type (might be due to invalid IL or missing references)
			//IL_0043: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Expected O, but got Unknown
			//IL_004f: Unknown result type (might be due to invalid IL or missing references)
			//IL_005b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0065: Expected O, but got Unknown
			//IL_0067: Unknown result type (might be due to invalid IL or missing references)
			//IL_0073: Unknown result type (might be due to invalid IL or missing references)
			//IL_007d: Expected O, but got Unknown
			//IL_007f: Unknown result type (might be due to invalid IL or missing references)
			//IL_008b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0095: Expected O, but got Unknown
			switch (connectionId)
			{
			case 1:
				((FrameworkElement)(AutoUpdateWindow)target).add_Loaded(new RoutedEventHandler(Window_Loaded));
				break;
			case 2:
				((UIElement)(Border)target).add_MouseLeftButtonDown(new MouseButtonEventHandler(Title_MouseLeftButtonDown));
				break;
			case 3:
				((ButtonBase)(Button)target).add_Click(new RoutedEventHandler(CloseButton_Click));
				break;
			case 4:
				((ButtonBase)(Button)target).add_Click(new RoutedEventHandler(RemindMeButton_Click));
				break;
			case 5:
				((ButtonBase)(Button)target).add_Click(new RoutedEventHandler(DownloadButton_Click));
				break;
			default:
				_contentLoaded = true;
				break;
			}
		}
	}
}
