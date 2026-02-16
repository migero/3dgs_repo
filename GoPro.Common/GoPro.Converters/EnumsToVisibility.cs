using System;
using System.Globalization;
using System.Windows;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class EnumsToVisibility : IMultiValueConverter
	{
		public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
		{
			int num = (int)values[0];
			for (int i = 1; i < values.Length; i++)
			{
				if (num == (int)values[i])
				{
					return (object)(Visibility)0;
				}
			}
			return (object)(Visibility)2;
		}

		public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
		{
			throw new NotImplementedException();
		}
	}
}
