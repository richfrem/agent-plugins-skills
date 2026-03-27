import { FormRules } from '../types/FormRules';
import { {APP_CODE}_Menu } from './{APP_CODE}_Menu';

export const {FORM_ID}_Rules: FormRules = {
    formId: '{FORM_ID}',
    title: '{APP_CODE} System',
    menu: {APP_CODE}_Menu,
    elements: {
{ELEMENTS_JSON}
    }
};

export default {FORM_ID}_Rules;
