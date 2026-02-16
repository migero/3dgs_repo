using System;
using System.CodeDom.Compiler;
using System.ComponentModel;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Markup;

namespace GoPro.Controls
{
	public class SliderPerformance : UserControl, INotifyPropertyChanged, IComponentConnector
	{
		public static readonly DependencyProperty TitleProperty = DependencyProperty.Register("Title", typeof(string), typeof(SliderPerformance), new PropertyMetadata((object)"", new PropertyChangedCallback(OnDependencyPropertyChangedCallBack)));

		public static readonly DependencyProperty PercentProperty = DependencyProperty.Register("Percent", typeof(double), typeof(SliderPerformance), new PropertyMetadata((object)0.0, new PropertyChangedCallback(OnDependencyPropertyChangedCallBack)));

		private bool _contentLoaded;

		public string Title
		{
			get
			{
				return (string)((DependencyObject)this).GetValue(TitleProperty);
			}
			set
			{
				((DependencyObject)this).SetValue(TitleProperty, (object)value);
			}
		}

		public double Percent
		{
			get
			{
				return (double)((DependencyObject)this).GetValue(PercentProperty);
			}
			set
			{
				((DependencyObject)this).SetValue(PercentProperty, (object)value);
			}
		}

		public event PropertyChangedEventHandler PropertyChanged;

		private static void OnDependencyPropertyChangedCallBack(DependencyObject sender, DependencyPropertyChangedEventArgs e)
		{
			((SliderPerformance)(object)sender).OnPropertyChanged(((DependencyPropertyChangedEventArgs)(ref e)).get_Property().get_Name());
		}

		public SliderPerformance()
		{
			InitializeComponent();
			((FrameworkElement)this).set_DataContext((object)this);
		}

		protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
		{
			this.PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
		}

		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		public void InitializeComponent()
		{
			if (!_contentLoaded)
			{
				_contentLoaded = true;
				Uri uri = new Uri("/GoPro.Common;component/controls/sliderperformance.xaml", UriKind.Relative);
				Application.LoadComponent((object)this, uri);
			}
		}

		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		[EditorBrowsable(EditorBrowsableState.Never)]
		void IComponentConnector.Connect(int connectionId, object target)
		{
			_contentLoaded = true;
		}
	}
}
