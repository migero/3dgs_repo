using System;
using System.Globalization;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class ThumbBorderWidthConverter : IValueConverter
	{
		public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
		{
			return int.Parse(parameter.ToString()) * 1000 / int.Parse(value.ToString());
		}

		public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
		{
			throw new NotImplementedException();
		}
	}
}
