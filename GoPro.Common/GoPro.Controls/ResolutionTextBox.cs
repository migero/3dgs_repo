using System;
using System.CodeDom.Compiler;
using System.ComponentModel;
using System.Diagnostics;
using System.Windows;
using System.Windows.Data;
using System.Windows.Markup;

namespace GoPro.Controls
{
	public class ResolutionTextBox : CustomControl, IComponentConnector
	{
		public static readonly DependencyProperty TextFallbackProperty = DependencyProperty.Register("TextFallback", typeof(string), typeof(ResolutionTextBox), new PropertyMetadata((object)null));

		public static readonly DependencyProperty ValueWidthProperty = DependencyProperty.Register("ValueWidth", typeof(double?), typeof(ResolutionTextBox), new PropertyMetadata((object)null, new PropertyChangedCallback(OnValueChangedCallBack)));

		public static readonly DependencyProperty ValueHeightProperty = DependencyProperty.Register("ValueHeight", typeof(double?), typeof(ResolutionTextBox), new PropertyMetadata((object)null, new PropertyChangedCallback(OnValueChangedCallBack)));

		private bool _contentLoaded;

		public string TextFallback
		{
			get
			{
				return (string)((DependencyObject)this).GetValue(TextFallbackProperty);
			}
			set
			{
				((DependencyObject)this).SetValue(TextFallbackProperty, (object)value);
			}
		}

		public double? ValueWidth
		{
			get
			{
				return (double?)((DependencyObject)this).GetValue(ValueWidthProperty);
			}
			set
			{
				((DependencyObject)this).SetValue(ValueWidthProperty, (object)value);
			}
		}

		public double? ValueHeight
		{
			get
			{
				return (double?)((DependencyObject)this).GetValue(ValueHeightProperty);
			}
			set
			{
				((DependencyObject)this).SetValue(ValueHeightProperty, (object)value);
			}
		}

		private static void OnValueChangedCallBack(DependencyObject sender, DependencyPropertyChangedEventArgs e)
		{
			BindingExpression bindingExpression = BindingOperations.GetBindingExpression(sender, ((DependencyPropertyChangedEventArgs)(ref e)).get_Property());
			if (bindingExpression != null)
			{
				((BindingExpressionBase)bindingExpression).UpdateTarget();
			}
		}

		public ResolutionTextBox()
		{
			InitializeComponent();
		}

		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		public void InitializeComponent()
		{
			if (!_contentLoaded)
			{
				_contentLoaded = true;
				Uri uri = new Uri("/GoPro.Common;component/controls/resolutiontextbox.xaml", UriKind.Relative);
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
			_contentLoaded = true;
		}
	}
}
