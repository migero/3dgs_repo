using System;
using System.CodeDom.Compiler;
using System.ComponentModel;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Markup;
using GoPro.Composition;
using GoPro.Instance;

namespace GoPro.Dialogs
{
	public class ProgressWindow : Window, IComponentConnector
	{
		public delegate void CanceledDelegate();

		public class Data
		{
			public string HeaderText;

			public uint Progress;

			public bool IsCancelVisible;
		}

		public static readonly DependencyProperty ProgressProperty = DependencyProperty.Register("Progress", typeof(uint), typeof(ProgressWindow), new PropertyMetadata((object)0u, new PropertyChangedCallback(OnProgressPropertyChangedCallBack)));

		private Data m_Data;

		internal EllipticalArcShape ArcShapeProgress;

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

		public uint Progress
		{
			get
			{
				return (uint)((DependencyObject)this).GetValue(ProgressProperty);
			}
			set
			{
				((DependencyObject)this).SetValue(ProgressProperty, (object)value);
				OnPropertyChanged("Progress");
			}
		}

		public bool IsCancelVisible
		{
			get
			{
				return m_Data.IsCancelVisible;
			}
			set
			{
				m_Data.IsCancelVisible = value;
				OnPropertyChanged("IsCancelVisible");
			}
		}

		public event CanceledDelegate Canceled;

		public event PropertyChangedEventHandler PropertyChanged;

		private static void OnProgressPropertyChangedCallBack(DependencyObject sender, DependencyPropertyChangedEventArgs e)
		{
			((ProgressWindow)(object)sender).ArcShapeProgress.AngularSize = 3.6 * (double)(uint)((DependencyPropertyChangedEventArgs)(ref e)).get_NewValue();
		}

		public ProgressWindow(string header, bool isCancelVisible = false)
		{
			m_Data = new Data();
			InitializeComponent();
			((FrameworkElement)this).set_DataContext((object)this);
			((Window)this).set_ShowInTaskbar(false);
			string arg = LocalizationService.Instance["LOC_GENERIC_DOTS"];
			HeaderText = $"{LocalizationService.Instance[header]}{arg}";
			IsCancelVisible = isCancelVisible;
			Progress = 0u;
		}

		protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
		{
			this.PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
		}

		private void Window_Loaded(object sender, RoutedEventArgs e)
		{
			VisualHelper.EnableBlur((Window)(object)this);
		}

		private void CancelButton_Click(object sender, RoutedEventArgs e)
		{
			if (this.Canceled != null)
			{
				this.Canceled();
			}
		}

		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		public void InitializeComponent()
		{
			if (!_contentLoaded)
			{
				_contentLoaded = true;
				Uri uri = new Uri("/GoPro.Common;component/dialogs/progresswindow.xaml", UriKind.Relative);
				Application.LoadComponent((object)this, uri);
			}
		}

		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		internal Delegate _CreateDelegate(Type delegateType, string handler)
		{
			return Delegate.CreateDelegate(delegateType, this, handler);
		}

		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		[EditorBrowsable(EditorBrowsableState.Never)]
		void IComponentConnector.Connect(int connectionId, object target)
		{
			//IL_0023: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Expected O, but got Unknown
			//IL_003c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0048: Unknown result type (might be due to invalid IL or missing references)
			//IL_0052: Expected O, but got Unknown
			switch (connectionId)
			{
			case 1:
				((FrameworkElement)(ProgressWindow)target).add_Loaded(new RoutedEventHandler(Window_Loaded));
				break;
			case 2:
				ArcShapeProgress = (EllipticalArcShape)target;
				break;
			case 3:
				((ButtonBase)(Button)target).add_Click(new RoutedEventHandler(CancelButton_Click));
				break;
			default:
				_contentLoaded = true;
				break;
			}
		}
	}
}
