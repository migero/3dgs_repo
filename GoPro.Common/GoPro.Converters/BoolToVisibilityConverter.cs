using System;
using System.Globalization;
using System.Windows;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class BoolToVisibilityConverter : IValueConverter
	{
		public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
		{
			bool num = (bool)(value ?? ((object)false));
			bool flag = bool.Parse((string)parameter);
			if (num != flag)
			{
				return (object)(Visibility)2;
			}
			return (object)(Visibility)0;
		}

		public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
		{
			throw new NotImplementedException();
		}
	}
}
