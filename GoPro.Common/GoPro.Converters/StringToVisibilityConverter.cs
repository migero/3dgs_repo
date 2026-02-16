using System;
using System.Globalization;
using System.Windows;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class StringToVisibilityConverter : IValueConverter
	{
		public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
		{
			if (value != null && !string.IsNullOrEmpty((string)value))
			{
				return (object)(Visibility)0;
			}
			return (object)(Visibility)2;
		}

		public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
		{
			throw new NotImplementedException();
		}
	}
}
