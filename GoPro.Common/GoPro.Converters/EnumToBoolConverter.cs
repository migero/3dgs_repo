using System;
using System.Globalization;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class EnumToBoolConverter : IValueConverter
	{
		public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
		{
			int num = ((value != null) ? ((int)value) : (-1));
			int num2 = (int)parameter;
			return num == num2;
		}

		public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
		{
			return Binding.DoNothing;
		}
	}
}
