using System;
using System.CodeDom.Compiler;
using System.ComponentModel;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Input;
using System.Windows.Markup;
using GoPro.Composition;
using GoPro.Instance;

namespace GoPro.Dialogs
{
	public class MessageWindow : Window, INotifyPropertyChanged, IComponentConnector
	{
		public enum Choice
		{
			CANCEL,
			NO,
			YES
		}

		public class Data
		{
			public string HeaderText;

			public string MessageText;

			public string CancelButtonText;

			public string NoButtonText;

			public string YesButtonText;

			public bool DoNotAskAgain;

			public Choice Selection;
		}

		private Data m_Data;

		internal StackPanel DoNotAskAgainPanel;

		internal Button CancelButton;

		internal Button NoButton;

		internal Button YesButton;

		private bool _contentLoaded;

		public string HeaderText
		{
			get
			{
				return m_Data.HeaderText;
			}
			set
			{
				m_Data.HeaderText = value;
				OnPropertyChanged("HeaderText");
			}
		}

		public string MessageText
		{
			get
			{
				return m_Data.MessageText;
			}
			set
			{
				m_Data.MessageText = value;
				OnPropertyChanged("MessageText");
			}
		}

		public string CancelButtonText
		{
			get
			{
				return m_Data.CancelButtonText;
			}
			set
			{
				m_Data.CancelButtonText = value;
				OnPropertyChanged("CancelButtonText");
			}
		}

		public string NoButtonText
		{
			get
			{
				return m_Data.NoButtonText;
			}
			set
			{
				m_Data.NoButtonText = value;
				OnPropertyChanged("NoButtonText");
			}
		}

		public string YesButtonText
		{
			get
			{
				return m_Data.YesButtonText;
			}
			set
			{
				m_Data.YesButtonText = value;
				OnPropertyChanged("YesButtonText");
			}
		}

		public bool DoNotAskAgain
		{
			get
			{
				return m_Data.DoNotAskAgain;
			}
			set
			{
				m_Data.DoNotAskAgain = value;
				OnPropertyChanged("DoNotAskAgain");
			}
		}

		public Choice Selection
		{
			get
			{
				return m_Data.Selection;
			}
			set
			{
				m_Data.Selection = value;
				OnPropertyChanged("Selection");
			}
		}

		public event PropertyChangedEventHandler PropertyChanged;

		public MessageWindow(string header, string message, string cancelButton, string noButton, string yesButton, bool showDoNotAskAgain, bool localized = true, params string[] arguments)
		{
			m_Data = new Data();
			InitializeComponent();
			((FrameworkElement)this).set_DataContext((object)this);
			((Window)this).set_ShowInTaskbar(false);
			if (showDoNotAskAgain)
			{
				((UIElement)DoNotAskAgainPanel).set_Visibility((Visibility)0);
			}
			HeaderText = GetText(header, localized);
			MessageText = GetText(message, localized);
			if (arguments.Length != 0)
			{
				string headerText = HeaderText;
				object[] args = arguments;
				HeaderText = string.Format(headerText, args);
				string messageText = MessageText;
				args = arguments;
				MessageText = string.Format(messageText, args);
			}
			if (cancelButton == null)
			{
				((UIElement)CancelButton).set_Visibility((Visibility)1);
			}
			else
			{
				CancelButtonText = GetText(cancelButton, localized);
			}
			if (noButton == null)
			{
				((UIElement)NoButton).set_Visibility((Visibility)1);
			}
			else
			{
				NoButtonText = GetText(noButton, localized);
			}
			YesButtonText = GetText(yesButton, localized);
			DoNotAskAgain = false;
		}

		protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
		{
			this.PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
		}

		private void Window_Loaded(object sender, RoutedEventArgs e)
		{
			VisualHelper.EnableBlur((Window)(object)this);
		}

		private string GetText(string key, bool localized)
		{
			if (!localized)
			{
				return key;
			}
			return LocalizationService.Instance[key];
		}

		private void Title_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
		{
			((Window)this).DragMove();
		}

		private void CloseButton_Click(object sender, RoutedEventArgs e)
		{
			((Window)this).Close();
		}

		private void CancelButton_Click(object sender, RoutedEventArgs e)
		{
			Selection = Choice.CANCEL;
			((Window)this).Close();
		}

		private void NoButton_Click(object sender, RoutedEventArgs e)
		{
			Selection = Choice.NO;
			((Window)this).Close();
		}

		private void YesButton_Click(object sender, RoutedEventArgs e)
		{
			Selection = Choice.YES;
			((Window)this).Close();
		}

		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		public void InitializeComponent()
		{
			if (!_contentLoaded)
			{
				_contentLoaded = true;
				Uri uri = new Uri("/GoPro.Common;component/dialogs/messagewindow.xaml", UriKind.Relative);
				Application.LoadComponent((object)this, uri);
			}
		}

		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		[EditorBrowsable(EditorBrowsableState.Never)]
		void IComponentConnector.Connect(int connectionId, object target)
		{
			//IL_0036: Unknown result type (might be due to invalid IL or missing references)
			//IL_0040: Expected O, but got Unknown
			//IL_0042: Unknown result type (might be due to invalid IL or missing references)
			//IL_004e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0058: Expected O, but got Unknown
			//IL_005a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0066: Unknown result type (might be due to invalid IL or missing references)
			//IL_0070: Expected O, but got Unknown
			//IL_0073: Unknown result type (might be due to invalid IL or missing references)
			//IL_007d: Expected O, but got Unknown
			//IL_0080: Unknown result type (might be due to invalid IL or missing references)
			//IL_008a: Expected O, but got Unknown
			//IL_0097: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a1: Expected O, but got Unknown
			//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ae: Expected O, but got Unknown
			//IL_00bb: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c5: Expected O, but got Unknown
			//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d2: Expected O, but got Unknown
			//IL_00df: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e9: Expected O, but got Unknown
			switch (connectionId)
			{
			case 1:
				((FrameworkElement)(MessageWindow)target).add_Loaded(new RoutedEventHandler(Window_Loaded));
				break;
			case 2:
				((UIElement)(Border)target).add_MouseLeftButtonDown(new MouseButtonEventHandler(Title_MouseLeftButtonDown));
				break;
			case 3:
				((ButtonBase)(Button)target).add_Click(new RoutedEventHandler(CloseButton_Click));
				break;
			case 4:
				DoNotAskAgainPanel = (StackPanel)target;
				break;
			case 5:
				CancelButton = (Button)target;
				((ButtonBase)CancelButton).add_Click(new RoutedEventHandler(CancelButton_Click));
				break;
			case 6:
				NoButton = (Button)target;
				((ButtonBase)NoButton).add_Click(new RoutedEventHandler(NoButton_Click));
				break;
			case 7:
				YesButton = (Button)target;
				((ButtonBase)YesButton).add_Click(new RoutedEventHandler(YesButton_Click));
				break;
			default:
				_contentLoaded = true;
				break;
			}
		}
	}
}
