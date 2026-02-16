using System;
using System.CodeDom.Compiler;
using System.ComponentModel;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using System.Text.RegularExpressions;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Input;
using System.Windows.Markup;

namespace GoPro.Controls
{
	public class NumericUpDown : UserControl, INotifyPropertyChanged, IComponentConnector
	{
		public static readonly DependencyProperty MinimumProperty = DependencyProperty.Register("Minimum", typeof(double), typeof(NumericUpDown), new PropertyMetadata((object)0.0, new PropertyChangedCallback(OnDependencyPropertyChangedCallBack)));

		public static readonly DependencyProperty MaximumProperty = DependencyProperty.Register("Maximum", typeof(double), typeof(NumericUpDown), new PropertyMetadata((object)0.0, new PropertyChangedCallback(OnDependencyPropertyChangedCallBack)));

		public static readonly DependencyProperty StepProperty = DependencyProperty.Register("Step", typeof(double), typeof(NumericUpDown), new PropertyMetadata((object)0.0, new PropertyChangedCallback(OnDependencyPropertyChangedCallBack)));

		public static readonly DependencyProperty ValueProperty = DependencyProperty.Register("Value", typeof(double), typeof(NumericUpDown), new PropertyMetadata((object)0.0, new PropertyChangedCallback(OnDependencyPropertyChangedCallBack)));

		public static readonly DependencyProperty CornerRadiusProperty = DependencyProperty.Register("CornerRadius", typeof(double), typeof(NumericUpDown), new PropertyMetadata((object)0.0, new PropertyChangedCallback(OnDependencyPropertyChangedCallBack)));

		internal TextBox TextBoxValue;

		private bool _contentLoaded;

		public double Minimum
		{
			get
			{
				return (double)((DependencyObject)this).GetValue(MinimumProperty);
			}
			set
			{
				((DependencyObject)this).SetValue(MinimumProperty, (object)value);
			}
		}

		public double Maximum
		{
			get
			{
				return (double)((DependencyObject)this).GetValue(MaximumProperty);
			}
			set
			{
				((DependencyObject)this).SetValue(MaximumProperty, (object)value);
			}
		}

		public double Step
		{
			get
			{
				return (double)((DependencyObject)this).GetValue(StepProperty);
			}
			set
			{
				((DependencyObject)this).SetValue(StepProperty, (object)value);
			}
		}

		public double Value
		{
			get
			{
				return (double)((DependencyObject)this).GetValue(ValueProperty);
			}
			set
			{
				((DependencyObject)this).SetValue(ValueProperty, (object)value);
			}
		}

		public double CornerRadius
		{
			get
			{
				return (double)((DependencyObject)this).GetValue(CornerRadiusProperty);
			}
			set
			{
				((DependencyObject)this).SetValue(CornerRadiusProperty, (object)value);
			}
		}

		public event PropertyChangedEventHandler PropertyChanged;

		public NumericUpDown()
		{
			InitializeComponent();
		}

		protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
		{
			this.PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
		}

		private static void OnDependencyPropertyChangedCallBack(DependencyObject sender, DependencyPropertyChangedEventArgs e)
		{
			((NumericUpDown)(object)sender).OnPropertyChanged(((DependencyPropertyChangedEventArgs)(ref e)).get_Property().get_Name());
		}

		private void TextBoxValue_KeyUp(object sender, KeyEventArgs e)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Invalid comparison between Unknown and I4
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0015: Expected O, but got Unknown
			if ((int)e.get_Key() == 6)
			{
				UpdateTextBoxValue((TextBox)sender);
			}
		}

		private void TextBoxValue_PreviewTextInput(object sender, TextCompositionEventArgs e)
		{
			Regex regex = new Regex("[^0-9]+");
			((RoutedEventArgs)e).set_Handled(regex.IsMatch(e.get_Text()));
		}

		private void TextBoxValue_LostKeyboardFocusEvent(object sender, RoutedEventArgs e)
		{
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Expected O, but got Unknown
			UpdateTextBoxValue((TextBox)sender);
		}

		private void ButtonIncrement_Click(object sender, RoutedEventArgs e)
		{
			Value = Math.Max(Math.Min(Value + Step, Maximum), Minimum);
		}

		private void ButtonDecrement_Click(object sender, RoutedEventArgs e)
		{
			Value = Math.Max(Math.Min(Value - Step, Maximum), Minimum);
		}

		private void UpdateTextBoxValue(TextBox textBox)
		{
			double val = double.Parse(textBox.get_Text());
			Value = Math.Max(Math.Min(val, Maximum), Minimum);
		}

		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		public void InitializeComponent()
		{
			if (!_contentLoaded)
			{
				_contentLoaded = true;
				Uri uri = new Uri("/GoPro.Common;component/controls/numericupdown.xaml", UriKind.Relative);
				Application.LoadComponent((object)this, uri);
			}
		}

		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		[EditorBrowsable(EditorBrowsableState.Never)]
		void IComponentConnector.Connect(int connectionId, object target)
		{
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0025: Expected O, but got Unknown
			//IL_0032: Unknown result type (might be due to invalid IL or missing references)
			//IL_003c: Expected O, but got Unknown
			//IL_0049: Unknown result type (might be due to invalid IL or missing references)
			//IL_0053: Expected O, but got Unknown
			//IL_0060: Unknown result type (might be due to invalid IL or missing references)
			//IL_006a: Expected O, but got Unknown
			//IL_006c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0078: Unknown result type (might be due to invalid IL or missing references)
			//IL_0082: Expected O, but got Unknown
			//IL_0084: Unknown result type (might be due to invalid IL or missing references)
			//IL_0090: Unknown result type (might be due to invalid IL or missing references)
			//IL_009a: Expected O, but got Unknown
			switch (connectionId)
			{
			case 1:
				TextBoxValue = (TextBox)target;
				((UIElement)TextBoxValue).add_KeyUp(new KeyEventHandler(TextBoxValue_KeyUp));
				((UIElement)TextBoxValue).add_PreviewTextInput(new TextCompositionEventHandler(TextBoxValue_PreviewTextInput));
				((UIElement)TextBoxValue).add_LostKeyboardFocus(new KeyboardFocusChangedEventHandler(TextBoxValue_LostKeyboardFocusEvent));
				break;
			case 2:
				((ButtonBase)(Button)target).add_Click(new RoutedEventHandler(ButtonIncrement_Click));
				break;
			case 3:
				((ButtonBase)(Button)target).add_Click(new RoutedEventHandler(ButtonDecrement_Click));
				break;
			default:
				_contentLoaded = true;
				break;
			}
		}
	}
}
