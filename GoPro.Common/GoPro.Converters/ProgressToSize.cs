using System;
using System.Globalization;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class ProgressToSize : IValueConverter
	{
		public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
		{
			double num = (double)(uint)value * 0.01;
			return double.Parse((string)parameter) * num;
		}

		public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
		{
			throw new NotImplementedException();
		}
	}
}
