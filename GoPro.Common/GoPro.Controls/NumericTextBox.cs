using System;
using System.CodeDom.Compiler;
using System.ComponentModel;
using System.Diagnostics;
using System.Text.RegularExpressions;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Input;
using System.Windows.Markup;

namespace GoPro.Controls
{
	public class NumericTextBox : CustomControl, IComponentConnector
	{
		public static readonly DependencyProperty TextFallbackProperty = DependencyProperty.Register("TextFallback", typeof(string), typeof(NumericTextBox), new PropertyMetadata((object)null));

		public static readonly DependencyProperty ValueProperty = DependencyProperty.Register("Value", typeof(double?), typeof(NumericTextBox), new PropertyMetadata((object)null, (PropertyChangedCallback)delegate(DependencyObject s, DependencyPropertyChangedEventArgs e)
		{
			((NumericTextBox)(object)s).OnPropertyChanged("Text");
		}));

		private static readonly Regex NUMERIC_REGEX = new Regex("[0-9]+");

		private bool mFocusTriggered;

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

		public double? Value
		{
			get
			{
				return (double?)((DependencyObject)this).GetValue(ValueProperty);
			}
			set
			{
				((DependencyObject)this).SetValue(ValueProperty, (object)value);
			}
		}

		public string Text
		{
			get
			{
				if (!Value.HasValue)
				{
					return TextFallback;
				}
				return Value.ToString();
			}
			set
			{
				double? value2 = null;
				double result = 0.0;
				if (double.TryParse(value, out result))
				{
					value2 = result;
				}
				Value = value2;
				OnPropertyChanged("Text");
			}
		}

		public NumericTextBox()
		{
			InitializeComponent();
		}

		private void TextBox_KeyUp(object sender, KeyEventArgs e)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Invalid comparison between Unknown and I4
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0015: Expected O, but got Unknown
			if ((int)e.get_Key() == 6)
			{
				UpdateCustomResolutionTexBox((TextBox)sender);
			}
		}

		private void TextBox_PreviewTextInput(object sender, TextCompositionEventArgs e)
		{
			((RoutedEventArgs)e).set_Handled(!IsNumeric(e.get_Text()));
		}

		private void TextBox_SelectionChanged(object sender, RoutedEventArgs e)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Expected O, but got Unknown
			TextBox val = (TextBox)sender;
			if (mFocusTriggered || !IsNumeric(val.get_Text()))
			{
				ForceSelection(val);
			}
			mFocusTriggered = false;
		}

		private void TextBox_GotFocus(object sender, RoutedEventArgs e)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Expected O, but got Unknown
			TextBox textBox = (TextBox)sender;
			ForceSelection(textBox);
			mFocusTriggered = true;
		}

		private void TextBox_LostFocus(object sender, RoutedEventArgs e)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Expected O, but got Unknown
			TextBox textBox = (TextBox)sender;
			UpdateCustomResolutionTexBox(textBox);
			mFocusTriggered = false;
		}

		private void UpdateCustomResolutionTexBox(TextBox textBox)
		{
			if (IsNumeric(textBox.get_Text()) && Text != textBox.get_Text())
			{
				Text = textBox.get_Text();
			}
		}

		private void ForceSelection(TextBox textBox)
		{
			//IL_0008: Unknown result type (might be due to invalid IL or missing references)
			//IL_0012: Expected O, but got Unknown
			//IL_0020: Unknown result type (might be due to invalid IL or missing references)
			//IL_002a: Expected O, but got Unknown
			((TextBoxBase)textBox).remove_SelectionChanged(new RoutedEventHandler(TextBox_SelectionChanged));
			((TextBoxBase)textBox).SelectAll();
			((TextBoxBase)textBox).add_SelectionChanged(new RoutedEventHandler(TextBox_SelectionChanged));
		}

		private bool IsNumeric(string text)
		{
			return NUMERIC_REGEX.IsMatch(text);
		}

		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		public void InitializeComponent()
		{
			if (!_contentLoaded)
			{
				_contentLoaded = true;
				Uri uri = new Uri("/GoPro.Common;component/controls/numerictextbox.xaml", UriKind.Relative);
				Application.LoadComponent((object)this, uri);
			}
		}

		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		[EditorBrowsable(EditorBrowsableState.Never)]
		void IComponentConnector.Connect(int connectionId, object target)
		{
			//IL_0005: Unknown result type (might be due to invalid IL or missing references)
			//IL_0011: Unknown result type (might be due to invalid IL or missing references)
			//IL_001b: Expected O, but got Unknown
			//IL_001c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0028: Unknown result type (might be due to invalid IL or missing references)
			//IL_0032: Expected O, but got Unknown
			//IL_0033: Unknown result type (might be due to invalid IL or missing references)
			//IL_003f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0049: Expected O, but got Unknown
			//IL_004a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0056: Unknown result type (might be due to invalid IL or missing references)
			//IL_0060: Expected O, but got Unknown
			//IL_0061: Unknown result type (might be due to invalid IL or missing references)
			//IL_006d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0077: Expected O, but got Unknown
			if (connectionId == 1)
			{
				((UIElement)(TextBox)target).add_KeyUp(new KeyEventHandler(TextBox_KeyUp));
				((UIElement)(TextBox)target).add_PreviewTextInput(new TextCompositionEventHandler(TextBox_PreviewTextInput));
				((TextBoxBase)(TextBox)target).add_SelectionChanged(new RoutedEventHandler(TextBox_SelectionChanged));
				((UIElement)(TextBox)target).add_GotFocus(new RoutedEventHandler(TextBox_GotFocus));
				((UIElement)(TextBox)target).add_LostFocus(new RoutedEventHandler(TextBox_LostFocus));
			}
			else
			{
				_contentLoaded = true;
			}
		}
	}
}
